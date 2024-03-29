# Gradio Login
OAuth login for Gradio. Currently supports only Google OAuth.

## Installation
```
pip install gradiologin
```
## Getting Started
1. Register a new OAuth app in Google Developer Dashboard

2. Use below code with your own client_id and client_secret
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

3. Host locally with `uvicorn app:app`
