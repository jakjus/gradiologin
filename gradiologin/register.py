import json
import gradio
from starlette.middleware.sessions import SessionMiddleware
from gradiologin.routes import providers, add_routes
from gradiologin.oauth import oauth
from gradiologin.middleware import add_middleware_redirect

def init(app, secret_key="some-secret-string", app_route='gradio', no_login_page=False):
    add_middleware_redirect(app, app_route)
    add_routes(app, app_route, no_login_page)
    app.add_middleware(SessionMiddleware, secret_key=secret_key)

def register(*args, **kwargs):
    providers.append(kwargs)
    return oauth.register(*args, **kwargs)

def mount_gradio_app(*args, secret_key="some-secret-string", no_login_page=False, **kwargs):
    # Proxy gradio's mount_gradio_app
    # to add authentication and routes
    app = args[0]
    path = args[2]
    init(app,
         secret_key,
         path,
         no_login_page)
    return gradio.mount_gradio_app(*args, **kwargs)
