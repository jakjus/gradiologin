from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from gradiologin.oauth import oauth
from fastapi.templating import Jinja2Templates
import gradiologin
import importlib.resources


providers = []

templates = Jinja2Templates(directory=importlib.resources.files(gradiologin).joinpath("templates"))

def add_routes(app, app_route, no_login_page=False):
    @app.get('/')
    async def homepage(request: Request):
        user = request.session.get('user')
        if user:
            return RedirectResponse(url=app_route)
        return RedirectResponse(url='login')

    if not no_login_page:
        @app.get('/login')
        async def login(request: Request):
            return templates.TemplateResponse(
                request=request, name="index.template.html", context={"providers": providers}
            )

    @app.get('/login/{provider_name}')
    async def login(request: Request, provider_name: str):
        client = oauth.create_client(provider_name)
        redirect_uri = request.url_for('auth', provider_name=provider_name)
        return await client.authorize_redirect(request, redirect_uri)

    @app.get('/auth/{provider_name}')
    async def auth(request: Request, provider_name: str):
        client = oauth.create_client(provider_name)
        try:
            token = await client.authorize_access_token(request)
        except OAuthError as error:
            return HTMLResponse(f'<h1>{error.error}</h1>')
        user = token.get('userinfo')
        if user:
            request.session['user'] = dict(user)
        return RedirectResponse(url='/')


    @app.get('/logout')
    async def logout(request: Request):
        request.session.pop('user', None)
        return RedirectResponse(url='/')
