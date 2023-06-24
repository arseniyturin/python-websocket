import ssl
import sys
import struct
import socket
import logging
from array import array
from typing import Any, Callable
from hashlib import sha1
from base64 import b64encode
import threading
from collections import deque

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

class API:
    """
    This class defines API methods for the developer to use

    Do not import it directly
    """

    def send(self, client: socket.socket, message: str) -> None:
        """Send message to client"""

        length = len(message.encode("utf8"))
        header = struct.pack("!B", FIN + OPCODE_TEXT)

        if length < 126:
            # ASCII
            payload_length = struct.pack("!B", length)

        if (length >= 126) and (length <= 65535):
            # ! - internet byte order (big endian)
            # B - unsigned char (1 byte)
            # H - unsigned short (2 bytes)
            payload_length = struct.pack("!BH", 126, length)

        if length > 65535:
            # ! - internet byte order (big endian)
            # B - unsigned char (1 byte)
            # Q - unsigned long long (8 bytes)
            payload_length = struct.pack("!BQ", 127, length)

        response = header + payload_length + message.encode("utf8")
        client.send(response)

    def sendall(self, message: str) -> None:
        """Send message to all clients"""

        for client in self.clients:
            try:
                self.send(client, message)
            except Exception as e:
                print("ERROR:", e)

    def onmessage(self, callback: Callable[[socket.socket, str], None]) -> None:
        """Incoming message to the server"""
        self._onmessage = callback

    def onopen(self, callback: Callable[[socket.socket], None]) -> None:
        """Client connected"""
        self._onopen = callback

    def onclose(self, callback: Callable[[socket.socket], None]) -> None:
        """Client left"""
        self._onclose = callback

    def onerror(self, callback: Callable[[socket.socket], None]) -> None:
        """TODO"""
        self._onerror = callback

    def close(self, client: socket.socket) -> None:
        """Close connection for particular client"""
        client.close()

    def shutdown(self) -> None:
        """Shutdown server"""
        self.sock.close()

    def _onmessage(self, client: socket.socket, message: str) -> None:
        """Placeholder for the user defined callback function"""
        pass

    def _onopen(self, client: socket.socket, message: str) -> None:
        """Placeholder for the user defined callback function"""
        pass

    def _onclose(self, client: socket.socket, message: str) -> None:
        """Placeholder for the user defined callback function"""
        pass

    def _onerror(self, client: socket.socket, message: str) -> None:
        """Placeholder for the user defined callback function"""
        pass