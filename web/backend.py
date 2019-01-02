import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.authentication import requires
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.endpoints import WebSocketEndpoint, HTTPEndpoint
from starlette.middleware.authentication import AuthenticationMiddleware

from handlers import handlers
from auth import BasicAuthBackend
from config import WS_HOST_PORT


app = Starlette(debug=True, template_directory='templates')
app.mount(app=StaticFiles(directory='assets'), path='/assets')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)
app.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend())


@app.route("/{endpoint}")
class Endpoint(HTTPEndpoint):

    async def get(self, request):
        try:
            endpoint = request.path_params['endpoint']
        except KeyError:
            endpoint = 'home'
        template = app.get_template(f'{endpoint}.html')
        content = template.render(request=request)
        return HTMLResponse(content)

    async def post(self, request):
        try:
            handler = request.path_params['endpoint']
        except KeyError:
            pass
        handler = handlers[handler]
        qp = request.query_params
        form = await request.form()

        # TODO may encounter unexpected issues here?!
        # TODO pass everything available handler, besides the two here
        resp = handler(query_params=qp,
                       form=form,
                       )
        return resp


@app.route("/")
class Home(HTTPEndpoint):
    async def get(self, request):
        username = 'anonymous'
        if request.user.is_authenticated:
            username = request.user.display_name
        try:
            username = request.cookies['test_cookies']
        except KeyError:
            pass

        props = {}
        props['username'] = username
        props['WS_HOST_PORT'] = WS_HOST_PORT

        template = app.get_template('home.html')
        content = template.render(request=request, props=props)
        resp = HTMLResponse(content)
        resp.set_cookie('member', username, expires=86400)
        return resp


@app.route("/me")
@requires(['authenticated', 'guest'], redirect='/')
class Me(HTTPEndpoint):
    async def get(self, request):
        # TODO
        pass
        return


@app.websocket_route("/")
class Broadcast(WebSocketEndpoint):

    encoding = "text"
    sessions = {}

    def update_sess_data(self, ws, data):
        session_key = ws.headers.get('sec-websocket-key', 'last')
        self.sessions[session_key] = ws
        print(self.sessions)

    async def broadcast_message(self, msg):
        for k in self.sessions:
            ws = self.sessions[k]
            await ws.send_text(f"{msg}")

    async def on_receive(self, ws, data):
        self.update_sess_data(ws, data)
        await self.broadcast_message(data)

    async def on_disconnect(self, websocket, close_code):
        self.sessions


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=20001)
