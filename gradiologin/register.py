import json
import gradio
from starlette.middleware.sessions import SessionMiddleware
from gradiologin.routes import add_routes
from gradiologin.oauth import oauth
from gradiologin.middleware import add_middleware_redirect


def init(app, secret_key="some-secret-string", app_route='gradio'):
    add_middleware_redirect(app, app_route)
    add_routes(app, app_route)
    app.add_middleware(SessionMiddleware, secret_key=secret_key)

def register(*args, **kwargs):
    # Does nothing for now
    return oauth.register(*args, **kwargs)

def mount_gradio_app(*args, secret_key=None, **kwargs):
    # Proxy gradio's mount_gradio_app 
    # to add authentication and routes
    app = args[0]
    path = args[2]
    init(app, secret_key, path)
    return gradio.mount_gradio_app(*args, **kwargs)
