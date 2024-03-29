from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth
import json
import gradio
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from gradiologin.routes import add_routes
from gradiologin.middleware import add_middleware_redirect

oauth = OAuth()

def get_user(request: gradio.Request):
    user = request.request.session.get('user')
    return user

def LogoutButton(*args, **kwargs):
    logout_js="window.location.href='/logout'"
    btn_logout = gradio.Button(*args, **kwargs)
    btn_logout.click(None, js=logout_js)
    return btn_logout
