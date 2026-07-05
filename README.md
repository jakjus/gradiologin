# gradiologin

[![PyPI](https://img.shields.io/pypi/v/gradiologin)](https://pypi.org/project/gradiologin/)
[![Python](https://img.shields.io/pypi/pyversions/gradiologin)](https://pypi.org/project/gradiologin/)
[![Tests](https://github.com/jakjus/gradiologin/actions/workflows/test.yml/badge.svg)](https://github.com/jakjus/gradiologin/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

OAuth / OpenID Connect login for [Gradio](https://gradio.app) apps. Put your entire Gradio app behind a "Sign in with Google" (or any OIDC provider) page with three lines of code.

- 🔒 **Everything protected** — every route, including the Gradio API, requires a login session
- 🧩 **Any OpenID Connect provider** — Google, Microsoft, Auth0, Keycloak, Okta, ...
- 🖥️ **Built-in login page** — clean, responsive, dark-mode aware, with provider brand icons; or bring your own
- 🪶 **Tiny API** — `register`, `mount_gradio_app`, `get_user`, `LogoutButton`

| Login page | Logged in |
|---|---|
| ![Login page](/screenshots/0_login_page.png) | ![App view](/screenshots/1_app.png) |

## Installation

```sh
pip install gradiologin
```

## Quickstart

```python
# app.py
import gradio as gr
import gradiologin as gl
from fastapi import FastAPI

app = FastAPI()

gl.register(
    name="google",
    icon="google",  # Font Awesome brand icon for the login button
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id="client_id_here",
    client_secret="client_secret_here",
    client_kwargs={"scope": "openid email profile"},
)

def show_user(request: gr.Request):
    user = gl.get_user(request)   # OpenID userinfo dict (email, name, picture, ...)
    return user

with gr.Blocks() as demo:
    btn_show = gr.Button("Get current user")
    databox = gr.JSON()
    btn_show.click(show_user, outputs=[databox])
    gl.LogoutButton("Logout")

gl.mount_gradio_app(app, demo, "/app", secret_key="replace-with-a-long-random-string")
```

Run it and open <http://localhost:8000>:

```sh
uvicorn app:app
```

Unauthenticated visitors are redirected to `/login`, pick a provider, authenticate, and land in your Gradio app. A complete runnable example lives in [`examples/app.py`](examples/app.py).

## API

### `gl.register(name, icon=None, **kwargs)`

Register an OAuth/OIDC provider. `name` becomes part of the routes (`/login/{name}`, `/auth/{name}`) and the login button label. `icon` is an optional [Font Awesome brand icon](https://fontawesome.com/search?f=brands) slug (e.g. `"google"`, `"github"`, `"microsoft"`). All other keyword arguments are passed to [Authlib](https://docs.authlib.org/en/latest/client/starlette.html) — typically `server_metadata_url`, `client_id`, `client_secret` and `client_kwargs`.

Call it multiple times to offer several providers on the login page:

```python
gl.register(
    name="keycloak",
    server_metadata_url="https://kc.example.com/realms/main/.well-known/openid-configuration",
    client_id="my-client",
    client_secret="...",
    client_kwargs={"scope": "openid email profile"},
)
```

### `gl.mount_gradio_app(app, blocks, path, ...)`

Drop-in replacement for `gradio.mount_gradio_app` that wires up sessions, the auth guard and the login/logout routes. Extra options on top of Gradio's:

| Option | Default | Description |
|---|---|---|
| `secret_key` | random per start | Key that signs the session cookie. **Set a stable random value in production**, otherwise sessions are invalidated on every restart and won't work with multiple workers. |
| `no_login_page` | `False` | Disable the built-in `/login` page. With one provider, `/login` redirects straight to it; with several, serve your own page linking to `/login/{provider_name}`. |
| `public_paths` | `()` | Path prefixes to leave unauthenticated, e.g. `["/health"]`. |

### `gl.get_user(request)`

Inside any Gradio event handler that takes a `gr.Request`, returns the OpenID userinfo `dict` of the logged-in user (keys depend on the provider and requested scopes — typically `email`, `name`, `picture`, `sub`).

### `gl.LogoutButton(*args, **kwargs)`

A `gr.Button` (same arguments) that clears the session and returns to the login page.

## Provider setup (Google example)

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) → *New Project*.
2. *APIs & Services → OAuth consent screen* → External → fill in the required fields.
3. *APIs & Services → Credentials → Create Credentials → OAuth Client ID*:
   - Application type: **Web application**
   - Authorized JavaScript origins: `http://localhost:8000`
   - Authorized redirect URIs: `http://localhost:8000/auth/google`
4. Save the `client_id` and `client_secret` and use them in `gl.register`.

In production, replace `http://localhost:8000` with your domain. The redirect URI is always `{origin}/auth/{provider_name}`.

Any provider that supports OpenID Connect discovery works the same way — just point `server_metadata_url` at its `/.well-known/openid-configuration`.

## Security notes

- Pass a **stable, secret** `secret_key` (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`) via an environment variable — it signs the session cookie.
- All routes on the FastAPI app are protected by default, including everything you add yourself. Use `public_paths` to opt specific prefixes out (health checks, webhooks, ...).
- Serve over HTTPS in production; OAuth providers require it for non-localhost redirect URIs.

## Development

```sh
git clone https://github.com/jakjus/gradiologin
cd gradiologin
pip install -e .[dev]
pytest
```

## License

[MIT](LICENSE)
