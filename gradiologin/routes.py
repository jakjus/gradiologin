from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from gradiologin.oauth import oauth


def add_routes(app, app_route):
    @app.get('/')
    async def homepage(request: Request):
        user = request.session.get('user')
        if user:
            return RedirectResponse(url=app_route)
        return RedirectResponse(url='login')

    @app.get('/login')
    async def login(request: Request):
        redirect_uri = request.url_for('auth')
        return await oauth.google.authorize_redirect(request, redirect_uri)

    @app.get('/logout')
    async def logout(request: Request):
        request.session.pop('user', None)
        return RedirectResponse(url='/')

    @app.get('/auth')
    async def auth(request: Request):
        try:
            token = await oauth.google.authorize_access_token(request)
        except OAuthError as error:
            return HTMLResponse(f'<h1>{error.error}</h1>')
        user = token.get('userinfo')
        if user:
            request.session['user'] = dict(user)
        return RedirectResponse(url='/')

