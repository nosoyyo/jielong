var ws = new WebSocket("ws://192.168.1.112:20001/");
ws.onmessage = function (event) {
    var messages = document.getElementById('messages')
    var message = document.createElement('li')
    var content = document.createTextNode(event.data)
    message.appendChild(content)
    messages.appendChild(message)
};
function sendMessage(event) {
    var name = document.getElementById('username').innerText
    var input = document.getElementById("msgText")
    ws.send(name + ': ' + input.value)
    input.value = ''
    event.preventDefault()
}
