import socket, threading, tkinter as tk
from DiffieHellman import DiffieHellman, key_to_string
from vigenere import Vigenere

PRIME = 23
BASE = 5

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Secure Chat Client")

        self.chat_log = tk.Text(master, state='disabled', width=60, height=20)
        self.chat_log.pack(padx=10, pady=10)

        self.msg_entry = tk.Entry(master, width=50)
        self.msg_entry.pack(side='left', padx=(10, 0), pady=(0, 10))
        self.msg_entry.bind("<Return>", self.send_message)

        self.send_btn = tk.Button(master, text="Send", command=self.send_message)
        self.send_btn.pack(side='left', padx=10, pady=(0, 10))

        self.key = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server()

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def connect_to_server(self, host='localhost', port=5555):
        self.sock.connect((host, port))

        dh = DiffieHellman(PRIME, BASE)
        self.sock.send(str(dh.pubKey).encode())
        server_pubkey = int(self.sock.recv(1024).decode())
        shared_secret = dh.calcSharedSecret(server_pubkey)
        self.key = key_to_string(shared_secret)

        self.display_message("🔐 Encrypted session established.\n")

    def receive_messages(self):
        while True:
            try:
                encrypted = self.sock.recv(1024).decode()
                if encrypted:
                    msg = Vigenere.vigenere_decrypt(encrypted, self.key)
                    self.display_message(msg)
            except:
                break

    def send_message(self, event=None):
        msg = self.msg_entry.get()
        if msg.strip():
            encrypted = Vigenere.vigenere_encrypt(msg, self.key)
            self.sock.send(encrypted.encode())
            self.display_message(f"You: {msg}")
            self.msg_entry.delete(0, tk.END)

    def display_message(self, msg):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, msg + '\n')
        self.chat_log.config(state='disabled')
        self.chat_log.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
