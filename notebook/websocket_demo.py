"""
fastapi.websocket官网演示: https://fastapi.tiangolo.com/advanced/websockets/
"""

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8401/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 等待该函数完成并返回结果, 等待异步函数完成时，协程会暂停执行，直到异步函数返回结果。
    # 您可以使用 await 关键字来等待该函数完成并返回结果。在等待异步函数完成时，协程会暂停执行，直到异步函数返回结果。
    # 使用await等待.accept()异步函数的返回结果: 如果一个函数是使用 async 关键字声明的异步函数，那么在调用该函数时，您必须使用 await 关键字等待该函数完成并返回结果。如果您不使用 await 关键字，那么该函数将返回一个协程对象，而不是实际的结果。
    # 这个函数总共有3步: 接收一个连接, 在这个连接下死循环，不断检测是否接受到文字，如果接收到data则将该数据send_text回去
    # 这个函数的每一步都是异步的，所以需要使用await等待每一步的完成
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

'''
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        ...
'''
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8401)