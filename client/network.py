# Connect to the server using sockets
# Send player input (movement)
# Receive synchronized game state updates

import socket
import json

class NetworkClient:
    def __init__(self, host="127.0.0.1", port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

    def send_input(self, dx, dy):
        data = {
            "type": "move",
            "dx": dx,
            "dy": dy
        }
        self.client.sendall(json.dumps(data).encode())

    def receive_state(self):
        try:
            data = self.client.recv(4096)
            if not data:
                return None
            return json.loads(data.decode())
        except:
            return None
