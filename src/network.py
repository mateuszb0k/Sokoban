from PyQt6.QtCore import Qt, QThread, pyqtSignal
import socket
import threading
import json
host = '127.0.0.1' #localhost
port = 12345
class Network(QThread):
    signal = pyqtSignal(dict)
    def __init__(self):
        QThread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
    def run(self):
        try:
            while True:
                data = self.socket.recv(4096)
                if data:
                    data = data.decode('utf-8')
                else:
                    break
                d = json.loads(data)
                self.signal.emit(d)
        except:
            print("Network error")
            self.socket.close()
    def send_data(self,payload):
        json_data = json.dumps(payload)
        data = json_data.encode('utf-8')
        self.socket.sendall(data)