"""Provider registration and the authenticated mount_gradio_app proxy."""

from __future__ import annotations

import secrets
import warnings
from typing import Iterable, Optional

import gradio
from starlette.middleware.sessions import SessionMiddleware

from gradiologin.middleware import add_auth_middleware
from gradiologin.oauth import oauth
from gradiologin.routes import add_routes, providers


def register(name: str, icon: Optional[str] = None, **kwargs):
    """Register an OAuth/OpenID Connect provider.

    Args:
        name: Provider name; used in the ``/login/{name}`` and
            ``/auth/{name}`` routes and on the login page button.
        icon: Optional Font Awesome brand icon slug shown on the login
            page button (e.g. ``"google"`` renders ``fa-google``).
        **kwargs: Passed through to Authlib's ``OAuth.register`` —
            typically ``server_metadata_url``, ``client_id``,
            ``client_secret`` and ``client_kwargs``.

    Returns:
        The Authlib remote app created for this provider.
    """
    providers.append({"name": name, "icon": icon, **kwargs})
    return oauth.register(name, **kwargs)


def init(
    app,
    secret_key: Optional[str] = None,
    app_route: str = "/gradio",
    no_login_page: bool = False,
    public_paths: Iterable[str] = (),
) -> None:
    """Attach session middleware, the auth guard and login routes to ``app``.

    Prefer :func:`mount_gradio_app`, which calls this for you.
    """
    if secret_key is None:
        secret_key = secrets.token_hex(32)
        warnings.warn(
            "gradiologin: no secret_key provided; a random one was generated. "
            "Sessions will not survive restarts and will not work across "
            "multiple workers. Pass secret_key= to mount_gradio_app().",
            stacklevel=3,
        )
    add_auth_middleware(app, public_paths)
    add_routes(app, app_route, no_login_page)
    # Added last so it wraps the auth middleware and the session is
    # already loaded when the auth check runs.
    app.add_middleware(SessionMiddleware, secret_key=secret_key)


def mount_gradio_app(
    app,
    blocks,
    path: str,
    *args,
    secret_key: Optional[str] = None,
    no_login_page: bool = False,
    public_paths: Iterable[str] = (),
    **kwargs,
):
    """Drop-in replacement for ``gradio.mount_gradio_app`` that requires login.

    Mounts ``blocks`` on ``app`` at ``path`` and protects the whole
    application: unauthenticated requests are redirected to ``/login``.

    Args:
        app: The FastAPI/Starlette application.
        blocks: The Gradio Blocks to mount.
        path: Mount path for the Gradio app (e.g. ``"/app"``).
        secret_key: Secret used to sign the session cookie. Set this to a
            stable random value in production; if omitted, a random key is
            generated at startup and existing sessions are invalidated on
            every restart.
        no_login_page: Disable the built-in ``/login`` provider-picker page.
            With a single registered provider, ``/login`` then redirects
            straight to it; with several, serve your own page that links to
            ``/login/{provider_name}``.
        public_paths: Extra path prefixes to leave unauthenticated
            (e.g. ``["/health"]``).
        *args, **kwargs: Passed through to ``gradio.mount_gradio_app``.
    """
    init(
        app,
        secret_key=secret_key,
        app_route=path,
        no_login_page=no_login_page,
        public_paths=public_paths,
    )
    return gradio.mount_gradio_app(app, blocks, path, *args, **kwargs)
