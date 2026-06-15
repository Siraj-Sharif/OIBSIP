import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, Entry, Button, simpledialog

class ChatGUI:
    def __init__(self, root):
        self.root = root
        root.title("Chat Client")
        
        # Ask for username before connecting
        self.username = simpledialog.askstring("Username", "Enter your name:", parent=root)
        if not self.username:
            root.destroy()
            return
        
        # Connect to server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('127.0.0.1', 5555))
        
        # Send username immediately
        self.client.send(self.username.encode('utf-8'))
        
        # Start receive thread
        threading.Thread(target=self.receive_messages, daemon=True).start()
        
        # Build UI
        self.text_area = scrolledtext.ScrolledText(root, state='disabled', width=50, height=20)
        self.text_area.pack(padx=10, pady=10)
        
        self.entry = Entry(root, width=40)
        self.entry.pack(side=tk.LEFT, padx=10, pady=10)
        self.entry.bind("<Return>", self.send_message)
        
        self.send_btn = Button(root, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT, padx=10)
    
    def receive_messages(self):
        while True:
            try:
                msg = self.client.recv(1024).decode('utf-8')
                self.text_area.config(state='normal')
                self.text_area.insert(tk.END, msg + "\n")
                self.text_area.config(state='disabled')
                self.text_area.see(tk.END)
            except:
                break
    
    def send_message(self, event=None):
        msg = self.entry.get()
        if msg:
            self.client.send(msg.encode('utf-8'))   # Send only the message
            self.entry.delete(0, tk.END)

root = tk.Tk()
app = ChatGUI(root)
root.mainloop()