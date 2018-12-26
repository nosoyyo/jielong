import uvicorn
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint, HTTPEndpoint
from starlette.responses import HTMLResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware


app = Starlette()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_headers=["*"], allow_methods=["*"]
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1 contenteditable='true' id='username'>click to change namet</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://192.168.1.112:20001/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var name = document.getElementById('username').innerText
                var input = document.getElementById("messageText")
                ws.send(name + ': ' + input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.route("/")
class Homepage(HTTPEndpoint):
    async def get(self, request):
        return HTMLResponse(html)


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
