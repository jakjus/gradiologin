"""Minimal gradiologin example with Google as the OAuth provider.

Setup:
    pip install gradiologin uvicorn python-dotenv
    export GOOGLE_CLIENT_ID=...
    export GOOGLE_CLIENT_SECRET=...
    export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
    uvicorn app:app

Then open http://localhost:8000
"""

import os

import gradio as gr
from fastapi import FastAPI

import gradiologin as gl

app = FastAPI()

gl.register(
    name="google",
    icon="google",  # Font Awesome brand icon on the login page
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    client_kwargs={"scope": "openid email profile"},
)


def greet(request: gr.Request):
    user = gl.get_user(request)
    return f"Welcome, {user['name']} ({user['email']})"


with gr.Blocks(title="gradiologin demo") as demo:
    greeting = gr.Textbox(label="Current user", interactive=False)
    btn = gr.Button("Who am I?")
    btn.click(greet, outputs=[greeting])
    gl.LogoutButton("Logout")

gl.mount_gradio_app(app, demo, "/app", secret_key=os.environ.get("SECRET_KEY"))
