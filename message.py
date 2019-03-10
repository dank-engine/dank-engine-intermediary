from enum import Enum

class MessageBuilder:
    def __init__(self):
        self._message = bytes()

    def add_command(self, command: bytes):
        """Adds a command to the message"""
        self._message += command

    def build_message(self) -> bytes:
        """Formats the message. Used before sending a message to the client"""
        return b'!%b$' % self._message


def build_off_command(id: int) -> bytes:
    return b'0,%d;' % id

def build_on_command(id: int, color: str) -> bytes:
    return b'1,%d,%x;' % (id, int(color, 16))

def build_flash_command(id: int, color: str) -> bytes:
    return b'2,%d,%x,255;' % (id, int(color, 16))

def build_fade_command(id: int, color: str, percentage: int) -> bytes:
    return b'3,%d,%x,%d;' % (id, int(color, 16), percentage)