# Gradio Login
OAuth Login for Gradio. Supports multiple OAuth Providers with a generic
login page.

## Installation

```sh
pip install gradiologin
```

## Getting Started

### Example Code

1. Use below code with your own OAuth details. You can get `client_id` and `client_secret` from your OAuth provider. (e.g. [OAuth App Registration](#oauth-app-registration))

```python3
# app.py

from fastapi import FastAPI
import gradio as gr
import gradiologin as gl

app = FastAPI()

# Google Provider
gl.register(
    name='google',
    icon='google',  # extra argument - refers to a brand icon
    # from Font Awesome (e.g. 'google' --> 'fa-google' icon)
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id='client_id_here',
    client_secret='client_secret_here',
    client_kwargs={
        'scope': 'openid email profile',
    },
)

# Custom OpenID Provider
gl.register(
    name='custom',
    server_metadata_url='http://localhost:8080/.well-known/openid-configuration',
    client_id='test',
    client_secret='abc',
    client_kwargs={
        'scope': 'openid email profile',
    },
)

def show_user(request: gr.Request):
    user = gl.get_user(request)
    return gr.update(value=user)

with gr.Blocks() as demo:
    btn_show = gr.Button("Get current user")
    databox = gr.Textbox(interactive=False)
    btn_show.click(show_user, outputs=[databox])

    gl.LogoutButton("Logout")

gradio_app = gl.mount_gradio_app(app, demo, "/app")

# add argument: 'no_login_page=True' to gl.mount_gradio_app
# to remove generic '/login' page
```

2. Host locally with `uvicorn app:app`
3. Navigate to `https://localhost:8000`

## Example App
Log in page
![Example 1](/screenshots/0_login_page.png)
Logged in view
![Example 2](/screenshots/1_app.png)

### OAuth App registration for Google Provider
Go to [Google Developer Console](https://console.cloud.google.com/)
1. *New Project > Create*
2. *APIs & Services > OAuth consent screen > External > Create*. Fill required fields.
3. *APIs & Services > Credentials > Create Credentials > OAuth Client ID*. Application type: Web application. Authorized JavaScript origins: `http://localhost:8000` for development. Authorized redirect URIs: `http://localhost:8000/login/google`, `http://localhost:8000/auth/google`. In production, change `http://localhost:8000` to your domain name. Save `client_id` and `client_secret`

