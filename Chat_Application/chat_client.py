import socket
import threading

def receive_messages(client):
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            print(f"\n{msg}")
        except:
            print("Disconnected from server")
            client.close()
            break

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 5555))
    
    # Send username FIRST
    username = input("Enter your name: ")
    client.send(username.encode('utf-8'))
    
    # Start receive thread
    thread = threading.Thread(target=receive_messages, args=(client,))
    thread.daemon = True
    thread.start()
    
    # Main send loop
    while True:
        msg = input()
        if msg.lower() == '/quit':
            client.close()
            break
        client.send(msg.encode('utf-8'))   # Send only the message, no "You:"

start_client()