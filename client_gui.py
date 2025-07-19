import socket, threading, tkinter as tk, tkinter.simpledialog as simpledialog
from tkinter import ttk
from DiffieHellman import DiffieHellman, key_to_string
from vigenere import Vigenere

PRIME = 23
BASE = 5

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Encrypted Messenger")
        self.master.configure(bg="#2c2f33")

        self.username = simpledialog.askstring("Username", "Enter your name:")
        if not self.username:
            self.master.destroy()
            return

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=1, fill='both')

        self.chat_tabs = {}  # username -> {frame, log, entry}
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

        encrypted_name = Vigenere.vigenere_encrypt(self.username, self.key)
        self.sock.send(encrypted_name.encode())

        self.display_message("everyone", "🔐 Encrypted session established.")
        self.ensure_tab("everyone")

    def receive_messages(self):
        while True:
            try:
                encrypted = self.sock.recv(1024).decode()
                if encrypted:
                    msg = Vigenere.vigenere_decrypt(encrypted, self.key)
                    if msg.startswith("SYSTEM:USERLIST:"):
                        users = msg.replace("SYSTEM:USERLIST:", "").split(",")
                        for user in users:
                            if user != self.username:
                                self.ensure_tab(user)
                    elif msg.startswith("(Private) "):
                        sender = msg.split()[1].split(":")[0]
                        self.display_message(sender, msg)
                    else:
                        sender = msg.split(":")[0]
                        self.display_message("everyone", msg)
            except:
                break

    def ensure_tab(self, username):
        if username not in self.chat_tabs:
            frame = ttk.Frame(self.notebook)
            chat_log = tk.Text(frame, state='disabled', wrap='word', bg="#2c2f33", fg="white")
            chat_log.pack(expand=1, fill='both')
            entry = tk.Entry(frame)
            entry.pack(side='left', fill='x', expand=True, padx=(10, 0), pady=5)
            entry.bind("<Return>", lambda event, u=username: self.send_message(u))
            send_btn = tk.Button(frame, text="Send", command=lambda u=username: self.send_message(u))
            send_btn.pack(side='left', padx=10, pady=5)
            self.chat_tabs[username] = {"frame": frame, "log": chat_log, "entry": entry}
            self.notebook.add(frame, text=username)

    def send_message(self, target):
        entry = self.chat_tabs[target]["entry"]
        msg = entry.get()
        if msg.strip():
            if target != "everyone":
                payload = f"TO:{target}:{msg}"
                display = f"You (to {target}): {msg}"
            else:
                payload = msg
                display = f"You: {msg}"
            encrypted = Vigenere.vigenere_encrypt(payload, self.key)
            self.sock.send(encrypted.encode())
            self.display_message(target, display)
            entry.delete(0, tk.END)

    def display_message(self, target, msg):
        self.ensure_tab(target)
        log = self.chat_tabs[target]["log"]
        log.config(state='normal')
        log.insert(tk.END, msg + '\n')
        log.config(state='disabled')
        log.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
