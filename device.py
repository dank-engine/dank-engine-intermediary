# [[RRRRR], [GGGGG], [BBBBB]] -> bytes(id, R_id, G_id, B_id, ...)
def convert_data(data) -> bytes:
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
        self.sock = socket.socket(socket.AF_INET, socket.SOC_DGRAM)

    def update(self, data: bytes) -> None:
        message = convert_data(data)
        self.sock.sendto(message, (self.ip_address, self.port))

class SerialDevice:
    def __init__(self, address: str, baud_rate: int) -> None:
        self.address = address
        self.baud_rate = baud_rate
        pass

    def update(self, data: bytes) -> None:
        message = []
        


