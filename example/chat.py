import sys
import socket
from collections import deque
from wsserver import WSServer

if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
    except IndexError:
        port = 8000

    # Keep last 10 messages for the new client
    latest_messages = deque(maxlen=10)

    # Keep set of clients
    clients = set()

    def onmessage(client: socket.socket, message: str, message_type: str) -> None:
        """
        Callback function for handling incoming messages from clients (browsers)

        Parameters:
            client (socket.socket): client that sent a message
            message (str | bytearray): message from a client
            message_type (str): type of a message: text, binary

        Returns:
            None
        """
        if message_type == "text":
            print(f"Message from {client.getpeername()}: {message}")
            latest_messages.append(message)
            ws.sendall(message)
        if message_type == "binary":
            print(f"Binary message: {message}")

    def onopen(client: socket.socket) -> None:
        """
        Callback function to handle new clients
        """
        print(f"Client connected: {client.getpeername()}")
        clients.add(client)
        if latest_messages:
            for message in latest_messages:
                ws.send(client, message)

    def onclose(client: socket.socket) -> None:
        """
        Callback function to handle clients that just left server
        """
        print(f"Client disconnected: {client.getpeername()}")
        clients.remove(client)

    ws = WSServer("", port)
    ws.onmessage(onmessage)
    ws.onopen(onopen)
    ws.onclose(onclose)
    ws.run()
