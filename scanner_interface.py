import socket
import json
import threading

class ScannerInterface:
    def __init__(self, port=65432):
        self.host = '127.0.0.1'
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.sock.setblocking(False)
        
        self.latest_data = {
            "player": {"x": 0, "y": 0, "z": 0, "yaw": 0, "pitch": 0},
            "blocks": []
        }
        self.running = True
        
        self.thread = threading.Thread(target=self._listen)
        self.thread.start()

    def _listen(self):
        print(f"Scanner Interface listening on {self.host}:{self.port}")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(65535)
                decoded = json.loads(data.decode('utf-8'))
                self.latest_data = decoded
            except BlockingIOError:
                pass # No data
            except Exception as e:
                print(f"Error receiving data: {e}")

    def get_data(self):
        return self.latest_data

    def stop(self):
        self.running = False
        self.sock.close()
