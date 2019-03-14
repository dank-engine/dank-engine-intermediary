import serial
import socket
import time


class SocketDevice:
    def __init__(self, ip_address: str, port: int) -> None:
        self.ip_address = ip_address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message: bytes) -> None:
        self.sock.sendto(message, (self.ip_address, self.port))


class SerialDevice:
    def __init__(self, port: str, baud_rate: int) -> None:
        self.serial = serial.Serial(port, baud_rate)
        self.serial.timeout = 1
        self.serial.rtscts = 1
        self.serial.close()
        time.sleep(2)
        self.serial.open()

    def send(self, message: bytes) -> None:
        assert len(message) < 128
        self.serial.write(message)


if __name__ == '__main__':
    # Sends hello world to serial
    device = SerialDevice('COM3', 19200)
    message = b'!1,1,255;$'
    message2 = b'!2,1,255;$'
    time.sleep(2)
    device.send(message)
    device.send(message2)
    device.serial.flush()
