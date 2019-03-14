import enum


class MessageType(enum.Enum):
    OFF = enum.auto()
    ON = enum.auto()
    FADE = enum.auto()
    FLASH = enum.auto()


class MessageBuilder:
    def __init__(self):
        self._message = bytes()

    def add_command(self, command: bytes):
        """Adds a command to the message"""
        self._message += command

    def build_message(self) -> bytes:
        """Formats the message. Used before sending a message to the client"""
        return b'!%b$' % self._message

    def clear_message(self) -> None:
        """Clears the current message."""
        self._message = bytes()


def build_off_command(id: int) -> bytes:
    return b'0,%d,0,0;' % id


def build_on_command(id: int, color: int) -> bytes:
    return b'1,%d,%d,0;' % (id, color)


def build_flash_command(id: int, color: int) -> bytes:
    return b'2,%d,%d,0;' % (id, color)


def build_fade_command(id: int, color: int, percentage: int) -> bytes:
    percentage = min(percentage, 255)
    percentage = max(percentage, 0)
    return b'3,%d,%d,%d;' % (id, color, percentage)
