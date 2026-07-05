"""OAuth / OpenID Connect login for Gradio apps.

Register one or more providers with :func:`register`, then mount your
Gradio Blocks with :func:`mount_gradio_app` instead of
``gradio.mount_gradio_app`` — every route is protected behind a login
session.
"""

from gradiologin.functions import LogoutButton, get_user
from gradiologin.register import init, mount_gradio_app, register

__version__ = "0.2.0"

__all__ = [
    "LogoutButton",
    "get_user",
    "init",
    "mount_gradio_app",
    "register",
    "__version__",
]
