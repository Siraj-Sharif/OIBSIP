import socket
import threading
from datetime import datetime

# Store connected clients: {socket: username}
clients = {}

def broadcast(message, sender_client=None):
    """Send message to all clients except the sender (if specified)."""
    for client in clients:
        if client != sender_client:
            try:
                client.send(message.encode('utf-8'))
            except:
                # Remove dead client
                del clients[client]

def handle_client(client):
    """Receive messages from a client and broadcast them."""
    try:
        username = client.recv(1024).decode('utf-8')
        clients[client] = username
        broadcast(f"{username} joined the chat!", sender_client=client)

        while True:
            msg = client.recv(1024).decode('utf-8')
            if not msg:
                break
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted = f"[{timestamp}] {username}: {msg}"
            broadcast(formatted, sender_client=client)
    except:
        pass
    finally:
        # Clean up on disconnect
        if client in clients:
            username = clients[client]
            del clients[client]
            broadcast(f"{username} left the chat.", sender_client=None)
        client.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5555))
    server.listen()
    print("✅ Server listening on 127.0.0.1:5555 ...")
    while True:
        client, addr = server.accept()
        print(f"📥 Connection from {addr}")
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    start_server()