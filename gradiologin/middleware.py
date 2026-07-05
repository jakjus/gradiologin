"""HTTP middleware that gates every route behind a login session."""

from __future__ import annotations

from typing import Iterable

from starlette.requests import Request
from starlette.responses import RedirectResponse

# Routes that must stay reachable without a session, otherwise
# nobody could ever log in (or out).
AUTH_PREFIXES = ("/login", "/auth", "/logout")


def add_auth_middleware(app, public_paths: Iterable[str] = ()) -> None:
    """Redirect unauthenticated requests to ``/login``.

    Every path is protected except the built-in auth routes and any
    prefixes listed in ``public_paths``.
    """
    public = tuple(public_paths)

    @app.middleware("http")
    async def check_authentication(request: Request, call_next):
        path = request.url.path
        if path.startswith(AUTH_PREFIXES) or (public and path.startswith(public)):
            return await call_next(request)

        if not request.session.get("user"):
            return RedirectResponse(url="/login")

        return await call_next(request)
