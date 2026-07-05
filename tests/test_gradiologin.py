"""Integration tests exercising the login flow with FastAPI's TestClient.

Providers are registered with explicit endpoint URLs (no
server_metadata_url) so no network access is ever needed.
"""

import itertools

import gradio as gr
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

import gradiologin as gl
from gradiologin.routes import providers

_counter = itertools.count()

USERINFO = {"email": "jane@example.com", "name": "Jane Doe"}


def build_app(provider_names=("acme",), **mount_kwargs):
    """Build a FastAPI app with fake provider(s) and a mounted Gradio app."""
    providers.clear()
    # Authlib keeps registered clients in a module-level registry, so give
    # every test its own provider names to avoid cross-test collisions.
    suffix = next(_counter)
    names = [f"{name}{suffix}" for name in provider_names]
    for name in names:
        gl.register(
            name=name,
            icon="github",
            client_id="test-client-id",
            client_secret="test-client-secret",
            authorize_url="https://idp.example.com/oauth/authorize",
            access_token_url="https://idp.example.com/oauth/token",
            client_kwargs={"scope": "openid email profile"},
        )

    app = FastAPI()

    @app.get("/testlogin")
    async def testlogin(request: Request):
        request.session["user"] = dict(USERINFO)
        return {"ok": True}

    with gr.Blocks() as demo:
        gr.Textbox(label="protected")

    mount_kwargs.setdefault("secret_key", "test-secret")
    mount_kwargs.setdefault("public_paths", ["/testlogin"])
    gl.mount_gradio_app(app, demo, "/app", **mount_kwargs)
    return app, names


@pytest.fixture
def client():
    app, names = build_app()
    with TestClient(app, follow_redirects=False) as c:
        c.provider_names = names
        yield c


def login(client):
    assert client.get("/testlogin").status_code == 200


def test_root_redirects_anonymous_to_login(client):
    response = client.get("/")
    assert response.status_code == 307
    assert response.headers["location"] == "/login"


def test_gradio_app_requires_login(client):
    response = client.get("/app")
    assert response.status_code == 307
    assert response.headers["location"] == "/login"


def test_gradio_api_requires_login(client):
    # The Gradio API must not be reachable without a session.
    response = client.post("/app/api/predict", json={})
    assert response.status_code == 307
    assert response.headers["location"] == "/login"


def test_login_page_lists_providers(client):
    response = client.get("/login")
    assert response.status_code == 200
    name = client.provider_names[0]
    assert f'href="/login/{name}"' in response.text
    assert f"Sign in with {name.capitalize()}" in response.text
    assert "fa-github" in response.text


def test_provider_login_redirects_to_authorize_url(client):
    name = client.provider_names[0]
    response = client.get(f"/login/{name}")
    assert response.status_code == 302
    location = response.headers["location"]
    assert location.startswith("https://idp.example.com/oauth/authorize")
    assert "client_id=test-client-id" in location


def test_unknown_provider_returns_404(client):
    assert client.get("/login/doesnotexist").status_code == 404
    assert client.get("/auth/doesnotexist").status_code == 404


def test_logged_in_user_reaches_gradio_app(client):
    login(client)
    response = client.get("/app/")
    assert response.status_code == 200


def test_root_redirects_logged_in_user_to_app(client):
    login(client)
    response = client.get("/")
    assert response.status_code == 307
    assert response.headers["location"] == "/app"


def test_logout_clears_session(client):
    login(client)
    response = client.get("/logout")
    assert response.status_code == 307
    assert response.headers["location"] == "/"
    # Session is gone: the app is protected again.
    response = client.get("/app")
    assert response.status_code == 307
    assert response.headers["location"] == "/login"


def test_no_login_page_single_provider_redirects_to_it():
    app, names = build_app(no_login_page=True)
    with TestClient(app, follow_redirects=False) as client:
        response = client.get("/login")
        assert response.status_code == 307
        assert response.headers["location"] == f"/login/{names[0]}"


def test_multiple_providers_on_login_page():
    app, names = build_app(provider_names=("acme", "globex"))
    with TestClient(app, follow_redirects=False) as client:
        response = client.get("/login")
        for name in names:
            assert f'href="/login/{name}"' in response.text


def test_missing_secret_key_warns():
    with pytest.warns(UserWarning, match="secret_key"):
        build_app(secret_key=None)


def test_get_user_returns_session_user():
    class FakeGradioRequest:
        class request:
            session = {"user": USERINFO}

    assert gl.get_user(FakeGradioRequest) == USERINFO


def test_get_user_returns_none_when_anonymous():
    class FakeGradioRequest:
        class request:
            session = {}

    assert gl.get_user(FakeGradioRequest) is None
