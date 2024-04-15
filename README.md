# Gradio Login
OAuth Login for Gradio. Currently supports only Google OAuth.

## Example App
OAuth Popup
![Example 1](/screenshots/0_oauth.png)
Logged in view
![Example 2](/screenshots/1_app.png)


## Installation
```
pip install gradiologin
```

## Getting Started
### Example Code
1. Use below code with your own Google OAuth `client_id` and `client_secret` (if you don't have it, go to [OAuth App Registration](#oauth-app-registration))

```python3
# app.py

from fastapi import FastAPI
import gradio as gr
import gradiologin as gl

app = FastAPI()
gl.register(
    name='google',
    server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration',
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
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
```

2. Host locally with `uvicorn app:app`
3. Navigate to `https://localhost:8000`

### OAuth App registration
Go to [Google Developer Console](https://console.cloud.google.com/)
1. *New Project > Create*
2. *APIs & Services > OAuth consent screen > External > Create*. Fill required fields.
3. *APIs & Services > Credentials > Create Credentials > OAuth Client ID*. Application type: Web application. Authorized JavaScript origins: `http://localhost:8000` for development. Authorized redirect URIs: `http://localhost:8000/login`, `http://localhost:8000/auth`. In production, change `http://localhost:8000` to your domain name. Save `client_id` and `client_secret`

