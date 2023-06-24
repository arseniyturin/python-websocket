import sys
sys.path.append('..')
from collections import deque
from wsserver import WSServer

if __name__ == '__main__':

    try:
        port = int(sys.argv[1])
    except IndexError:
        port = 8000

    # keep last 10 messages for the new client
    latest_messages = deque(maxlen=10)

    # User defined function for handling incoming messages
    # Must take two parameters: client and message
    def onmessage_(client, message):
        print('Message:', message)
        latest_messages.append(message)
        ws.sendall(message)

    # User defined function for handling client that joined
    # Must take one parameter: client
    def onopen_(client):
        print('Client connected')
        if latest_messages:
            for message in latest_messages:
                ws.send(client, message)

    # User defined function for handling client that left
    # Must take one parameter: client
    def onclose_(client):
        print('Client disconnected')

    ws = WSServer('', port)
    ws.onmessage(onmessage_)
    ws.onopen(onopen_)
    ws.onclose(onclose_)
    ws.run()