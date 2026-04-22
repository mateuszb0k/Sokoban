import socket
import threading
import json
host = '127.0.0.1' #localhost
port = 12345

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
server.listen()
clients = []
def broadcast(msg,org_client):
    for client in clients:
        if client is not org_client:
            client.sendall(msg)
        else:
            pass
def handle(client):
    try:
        while True:
            data = client.recv(4096)
            if data:
                broadcast(data,client)
            else:
                client.close()
                clients.remove(client)
                break
    except:
        client.close()
        if client in clients:
            clients.remove(client)
        else:
            pass
def receive():
    while True:
        client, addr = server.accept()
        clients.append(client)
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
if __name__ == '__main__':
    receive()
    server.close()
