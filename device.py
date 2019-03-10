import serial
import socket
import time 

# [[RRRRR], [GGGGG], [BBBBB]] -> bytes(id, R_id, G_id, B_id, ...)
def convert_data(data) -> bytes:
    message = []
    for i in range(data):
        message.append(i)
        message.append(data[0][i])
        message.append(data[1][i])
        message.append(data[2][i])
    return bytes(message)
    
class SocketDevice:
    def __init__(self, ip_address: str, port: int) -> None:
        self.ip_address = ip_address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def update(self, data: bytes) -> None:
        message = convert_data(data)
        self.sock.sendto(message, (self.ip_address, self.port))

class SerialDevice:
    def __init__(self, port: str = 'COM3', baud_rate: int = 19200) -> None:
        self.serial = serial.Serial()
        self.serial.baudrate = 19200
        self.serial.port = 'COM3'
        self.serial.timeout = 1
        self.serial.rtscts = 1
        time.sleep(2)
        self.serial.open()

    def send(self, message: bytes) -> None:
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
