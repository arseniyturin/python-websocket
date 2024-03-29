"""
  0                   1                   2                   3
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 +-+-+-+-+-------+-+-------------+-------------------------------+
 |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
 |I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
 |N|V|V|V|       |S|             |   (if payload len==126/127)   |
 | |1|2|3|       |K|             |                               |
 +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
 |   Extended payload length continued, if payload len == 127    |
 + - - - - - - - - - - - - - - - +-------------------------------+
 |                               | Masking-key, if MASK set to 1 |
 +-------------------------------+-------------------------------+
 | Masking-key (continued)       |          Payload Data         |
 +-------------------------------- - - - - - - - - - - - - - - - +
 :                     Payload Data continued ...                :
 + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
 |                     Payload Data continued ...                |
 +---------------------------------------------------------------+
"""

import ssl
import sys
import socket
from array import array
from hashlib import sha1
from base64 import b64encode
import threading
from .api import API
from .logger import get_logger

FIN = 0x80
MASK = 0x80
OPCODE_CONTINUATION = 0x0
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xA
PAYLOAD_LENGTH = 0x7D
PAYLOAD_LENGTH_EXT16 = 0x7E
PAYLOAD_LENGTH_EXT64 = 0x7F

logger = get_logger("console_and_file")


class WSServer(API):
    """
    WebSocket Server that uses threads to handle multiple clients

    Args:
        host: default ''
        port: default 8000
        cert: TLS certificate, default None
        key: private key, default None

    Returns:
        Server object with following methods:
            - send()
            - sendall()
            - onopen()
            - onclose()
            - onmessage()
            - close()
            - shutdown()
            - run()
            - clients
    """

    def __init__(self, host="", port=8000, cert=None, key=None):
        self.host = host
        self.port = port
        self.cert = cert
        self.key = key
        self.clients = set()
        self.message_types = {
            OPCODE_TEXT: "text",
            OPCODE_BINARY: "binary",
            OPCODE_CONTINUATION: "continuation",
            OPCODE_CLOSE: "close",
            OPCODE_PING: "ping",
            OPCODE_PONG: "pong",
        }

        def __call__(self):
            pass

        def __str__(self):
            return "WSServer by Arseny Turin"

        def __repr__(self):
            return "WSServer by Arseny Turin"

    def run(self):
        """Run server forever"""

        if self.cert and self.key:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(self.cert, self.key)

        try:
            # AF_INET - IPv4 family
            # SOCK_STREAM - TPC connection
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                self.sock = sock
                # Reuse same port if connection is broken
                # SOL_SOCKET - 65535
                # SO_REUSEADDR - 4
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # Bind the socket to a local address
                sock.bind((self.host, self.port))
                # Start listening for clients
                sock.listen(5)
                # Print ip address of the host
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)

                print(f"Server started on http://{ip}:{self.port} ")

                while True:
                    # Accepting client (socket)
                    client, address = sock.accept()
                    # Wrap socket into SSL context
                    # Client app would have to use wss://.. instead of ws://..
                    if self.cert and self.key:
                        client = context.wrap_socket(client, server_side=True)
                    # Put each client to the separate thread
                    # _handle_client is the function that will handle
                    # everything client related
                    threading.Thread(
                        target=self._handle_client, args=(address, client), daemon=True
                    ).start()

        except KeyboardInterrupt:
            # Stop server, close socket
            print("", end="\r")
            print("Exiting..")
            sock.close()

    def _handshake(self, frame: bytes, client: socket.socket) -> None:
        """Upgrade from HTTP to WebSocket protocol"""
        headers = frame.decode("utf8").split("\n")
        for header in headers:
            if header.startswith("Sec-WebSocket-Key"):
                key = header.replace("Sec-WebSocket-Key:", "").strip()
                accept_key = self._generate_accept_key(key)
                response = (
                    "HTTP/1.1 101 Switching Protocols\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Accept: {accept_key}\r\n\r\n"
                )
                client.send(response.encode("utf8"))

    def _generate_accept_key(self, key: str) -> bytes:
        """
        Proper way to establish WebSocket connection

        >>> _generate_accept_key('dGhlIHNhbXBsZSBub25jZQ==')
        s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
        """
        GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        sha1_hash = sha1((key + GUID).encode("utf8")).digest()
        return b64encode(sha1_hash).decode("utf8")

    def _recvall(self, client: socket.socket, size=1024) -> bytes:
        """Receive full message from the client"""

        message = bytearray()
        while True:
            chunk = client.recv(size)
            message += chunk
            if len(chunk) < size:
                break
        return message

    def _unmask_message(
        self,
        message_opcode: int,
        masking_key: bytearray,
        payload_data: bytearray,
    ) -> tuple:
        """Unmask message"""

        # Message type: text, binary, close, etc
        message_type = self.message_types[message_opcode]
        # Fast appending with bytearray
        message = bytearray()
        # Unmask payload
        if payload_data is not None:
            for byte in range(len(payload_data)):
                message.append(payload_data[byte] ^ masking_key[byte % 4])

        return message_type, message

    def _process_message(
        self, client: socket.socket, message_type: str, message: bytearray
    ) -> None:
        """
        Take action based on message type
        """
        # If message is text, decode and call callback function
        if message_type == "text":
            self._onmessage(client, message.decode("utf8"), message_type)

        # If message is binary, call callback function
        if message_type == "binary":
            self._onmessage(client, bytes(message), message_type)

        # Client left, closing his thread and removing from the list
        if message_type == "close":
            self.clients.remove(client)
            self._onclose(client)
            sys.exit()

    def _handle_frame(self, client: socket.socket, frame: bytearray) -> tuple:
        """Deciding what to do with the frame"""
        # OPCODE for frame type (text, binary, ...)
        message_opcode = frame[0] & 0xF
        # Payload length
        payload = frame[1] & 0x7F

        # Message size below 126 bytes
        if payload <= PAYLOAD_LENGTH:
            masking_key = frame[2:6]
            payload_data = frame[6:]

        # Message size from 126 to 65535 bytes
        if payload == PAYLOAD_LENGTH_EXT16:
            masking_key = frame[4:8]
            payload_data = frame[8:]

        # Message size from 65535 bytes to (2^64)-1 bytes
        if payload == PAYLOAD_LENGTH_EXT64:
            masking_key = frame[10:14]
            payload_data = frame[14:]

        message_type, message = self._unmask_message(
            message_opcode, masking_key, payload_data
        )
        self._process_message(client, message_type, message)

    def _handle_client(self, address: str, client: socket.socket) -> None:
        """Handshake new client or process WebSocket frame"""

        while True:
            frame = self._recvall(client, 2048)
            if frame:
                # If client is already connected, process message
                if client in self.clients:
                    self._handle_frame(client, frame)
                # New client, perform handshake and upgrade to WebSocket protocol
                else:
                    self._handshake(frame, client)
                    self.clients.add(client)
                    self._onopen(client)
