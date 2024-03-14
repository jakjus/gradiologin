from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth
import json
import gradio
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from routes import add_routes
from middleware import add_middleware_redirect

oauth = OAuth()

def get_user(request: gradio.Request):
    user = request.request.session.get('user')
    return user
