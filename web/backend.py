import uvicorn
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint, HTTPEndpoint
from starlette.responses import HTMLResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request


app = Starlette(debug=True, template_directory='templates')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)


@app.route("/")
class Homepage(HTTPEndpoint):
    async def get(self, request):
        template = app.get_template('index.html')
        content = template.render(request=request,)
        return HTMLResponse(content)


@app.websocket_route("/ws")
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=20001)
