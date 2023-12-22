import struct
import socket
from .logger import get_logger
from typing import Callable

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


class API:
    """
    This class defines API methods for the developer to use

    Do not import it directly
    """

    def send(self, client: socket.socket, message: str) -> None:
        """Send text message to client"""

        if isinstance(message, str):
            message = message.encode("utf8")
            length = len(message)
            header = struct.pack("!B", FIN + OPCODE_TEXT)
        else:
            length = len(message)
            header = struct.pack("!B", FIN + OPCODE_BINARY)

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

        response = header + payload_length + message
        client.send(response)

    def sendall(self, message: str) -> None:
        """Send text message to all clients"""

        for client in self.clients:
            try:
                self.send(client, message)
            except Exception as e:
                logger.error(f"Failed to send message: {e}", exc_info=True)

    def onmessage(self, callback: Callable[[socket.socket, str, str], None]) -> None:
        """Incoming message to the server"""
        self._onmessage = callback

    def onopen(self, callback: Callable[[socket.socket], None]) -> None:
        """Client connected"""
        self._onopen = callback

    def onclose(self, callback: Callable[[socket.socket], None]) -> None:
        """Client disconnected"""
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

    def _onmessage(
        self, client: socket.socket, message: str, message_type: str = "text"
    ) -> None:
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
