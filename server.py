import socket
import threading

clients = {}  # {client_socket: username}

def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            client.send(message.encode())

def handle_client(client_socket):
    username = client_socket.recv(1024).decode()
    clients[client_socket] = username
    print(f"{username} bağlandı.")

    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg.startswith("@"):  # Unicast
                target_user, user_msg = msg[1:].split(":", 1)
                for sock, name in clients.items():
                    if name == target_user:
                        sock.send(f"[Unicast {username}]: {user_msg}".encode())
            else:
                broadcast(f"[{username}]: {msg}", client_socket)
        except:
            print(f"{username} bağlantısı kesildi.")
            client_socket.close()
            del clients[client_socket]
            break

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 5555))
server.listen()

print("Server çalışıyor...")

while True:
    client_socket, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket,))
    thread.start()

