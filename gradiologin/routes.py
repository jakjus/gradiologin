"""FastAPI routes for the login flow: login page, OAuth redirect,
callback and logout."""

from __future__ import annotations

import html
import importlib.resources
from typing import Any, Dict, List

from authlib.integrations.starlette_client import OAuthError
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from gradiologin.oauth import oauth

# Providers registered via gradiologin.register(); rendered on the login page.
providers: List[Dict[str, Any]] = []

templates = Jinja2Templates(
    directory=str(importlib.resources.files("gradiologin").joinpath("templates"))
)


def add_routes(app, app_route: str, no_login_page: bool = False) -> None:
    @app.get("/", include_in_schema=False)
    async def homepage(request: Request):
        if request.session.get("user"):
            return RedirectResponse(url=app_route)
        return RedirectResponse(url="/login")

    if not no_login_page:

        @app.get("/login", include_in_schema=False)
        async def login_page(request: Request):
            return templates.TemplateResponse(
                request=request,
                name="index.template.html",
                context={"providers": providers},
            )

    elif len(providers) == 1:
        # No login page wanted and only one provider: skip straight
        # to that provider instead of 404-ing on /login.
        @app.get("/login", include_in_schema=False)
        async def login_redirect(request: Request):
            return RedirectResponse(url=f"/login/{providers[0]['name']}")

    @app.get("/login/{provider_name}", include_in_schema=False)
    async def provider_login(request: Request, provider_name: str):
        client = oauth.create_client(provider_name)
        if client is None:
            return HTMLResponse(
                f"<h1>Unknown provider: {html.escape(provider_name)}</h1>",
                status_code=404,
            )
        redirect_uri = request.url_for("auth", provider_name=provider_name)
        return await client.authorize_redirect(request, str(redirect_uri))

    @app.get("/auth/{provider_name}", include_in_schema=False)
    async def auth(request: Request, provider_name: str):
        client = oauth.create_client(provider_name)
        if client is None:
            return HTMLResponse(
                f"<h1>Unknown provider: {html.escape(provider_name)}</h1>",
                status_code=404,
            )
        try:
            token = await client.authorize_access_token(request)
        except OAuthError as error:
            return HTMLResponse(
                f"<h1>Authentication failed</h1><p>{html.escape(str(error))}</p>",
                status_code=401,
            )
        user = token.get("userinfo")
        if user:
            request.session["user"] = dict(user)
        return RedirectResponse(url="/")

    @app.get("/logout", include_in_schema=False)
    async def logout(request: Request):
        request.session.pop("user", None)
        return RedirectResponse(url="/")
