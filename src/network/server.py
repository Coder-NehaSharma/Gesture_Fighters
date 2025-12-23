import socket
import threading
import struct
from src.network.utils import deserialize_landmarks, recvall

class MultiPlayerServer:
    """
    Host Server running on Mac.
    Accepts up to 2 clients:
    - First connection = Player 1
    - Second connection = Player 2
    """
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        
        # State
        self.p1_socket = None
        self.p2_socket = None
        
        self.latest_p1_landmarks = None
        self.latest_p2_landmarks = None
        
        self.lock = threading.Lock()

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)
        self.running = True
        
        print(f"Server Host: Listening on {self.host}:{self.port}")
        
        # Start connection acceptor thread
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        print("Waiting for players to connect...")
        while self.running:
            try:
                client, addr = self.server_socket.accept()
                print(f"Incoming connection from {addr}")
                
                # Assign Roles based on First-Come-First-Serve
                if self.p1_socket is None:
                    print(f"-> Assigned as PLAYER 1")
                    self.p1_socket = client
                    threading.Thread(target=self._handle_client, args=(client, 1), daemon=True).start()
                
                elif self.p2_socket is None:
                    print(f"-> Assigned as PLAYER 2")
                    self.p2_socket = client
                    threading.Thread(target=self._handle_client, args=(client, 2), daemon=True).start()
                    
                else:
                    print("-> Lobby Full. Rejecting.")
                    client.close()
            except Exception as e:
                print(f"Accept error: {e}")

    def _handle_client(self, sock, player_id):
        while self.running:
            try:
                # 1. Read Length (4 bytes)
                raw_msglen = recvall(sock, 4)
                if not raw_msglen: break
                msglen = struct.unpack('>I', raw_msglen)[0]
                
                # 2. Read Data
                data = recvall(sock, msglen)
                if not data: break
                
                # 3. Process
                landmarks = deserialize_landmarks(data)
                
                with self.lock:
                    if player_id == 1:
                        self.latest_p1_landmarks = landmarks
                    else:
                        self.latest_p2_landmarks = landmarks
                        
            except Exception as e:
                print(f"Player {player_id} disconnected: {e}")
                break
        
        # Cleanup
        with self.lock:
            if player_id == 1: 
                self.p1_socket = None
                self.latest_p1_landmarks = None
            else: 
                self.p2_socket = None
                self.latest_p2_landmarks = None
        
        sock.close()
        print(f"Player {player_id} socket closed.")

    def get_landmarks(self):
        with self.lock:
            return self.latest_p1_landmarks, self.latest_p2_landmarks

    def stop(self):
        self.running = False
        if self.p1_socket: self.p1_socket.close()
        if self.p2_socket: self.p2_socket.close()
        if self.server_socket: self.server_socket.close()
