"""Helpers for use inside Gradio Blocks: current user and logout button."""

from __future__ import annotations

from typing import Any, Dict, Optional

import gradio


def get_user(request: gradio.Request) -> Optional[Dict[str, Any]]:
    """Return the OpenID userinfo of the logged-in user, or ``None``.

    Use it in an event handler that receives a ``gr.Request``::

        def greet(request: gr.Request):
            user = gl.get_user(request)
            return f"Hello {user['name']}"
    """
    return request.request.session.get("user")


def LogoutButton(*args, logout_url: str = "/logout", **kwargs) -> gradio.Button:
    """A ``gr.Button`` that logs the user out and returns to the login page.

    Accepts the same arguments as ``gr.Button``.
    """
    btn_logout = gradio.Button(*args, **kwargs)
    btn_logout.click(None, js=f"window.location.href='{logout_url}'")
    return btn_logout
