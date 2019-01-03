//创建ws连接  
function connectSocket(host) {
    var host = "ws://192.168.1.112:20001/"
    window.ws = new WebSocket(host);
    /*建立连接*/
    ws.onopen = evt => {
        console.log("ws连接成功");
    };
    /*连接关闭*/
    ws.onclose = evt => {
        console.log("ws连接关闭");
    };
    /*接收服务器推送消息*/
    ws.onmessage = evt => {
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
    };
    window.sendMessage = sendMessage;

    /*连接发生错误时*/
    ws.onerror = (evt, e) => {
        console.log(evt);
    };
}

window.onload = connectSocket
