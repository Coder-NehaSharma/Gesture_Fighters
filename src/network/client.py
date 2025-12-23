import socket
import struct
import time
from src.network.utils import serialize_landmarks

class GameClient:
    def __init__(self, host_ip, port=5000):
        self.host_ip = host_ip
        self.port = port
        self.socket = None
        self.connected = False

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host_ip, self.port))
            self.connected = True
            print(f"Connected to Host at {self.host_ip}:{self.port}")
            return True
        except Exception as e:
            print(f"Could not connect to Host: {e}")
            return False

    def send_landmarks(self, landmarks):
        if not self.connected:
            return

        try:
            # 1. Serialize
            data = serialize_landmarks(landmarks)
            
            # 2. Prefix with length (4 bytes big-endian)
            # This ensures we define packet boundaries clearly
            msg = struct.pack('>I', len(data)) + data
            
            # 3. Send
            self.socket.sendall(msg)
            
        except BrokenPipeError:
            print("Server disconnected.")
            self.connected = False
        except Exception as e:
            print(f"Send error: {e}")
            self.connected = False

    def close(self):
        if self.socket:
            self.socket.close()
