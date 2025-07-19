import socket, threading, tkinter as tk, tkinter.simpledialog as simpledialog

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.username = simpledialog.askstring("Username", "Enter your name:")
        if not self.username:
            self.master.destroy()
            return
        self.master.title(f"Messenger – {self.username}")
        self.master.configure(bg="#2c2f33")

        self.chat_logs = {}  # username -> Text widget
        self.active_chat = "everyone"

        self.left_frame = tk.Frame(master, width=150, bg="#23272a")
        self.left_frame.pack(side='left', fill='y')

        self.contacts_label = tk.Label(self.left_frame, text="Contacts", bg="#23272a", fg="white")
        self.contacts_label.pack(pady=5)

        self.contact_listbox = tk.Listbox(self.left_frame, bg="#2c2f33", fg="white")
        self.contact_listbox.pack(fill='y', expand=True, padx=5)
        self.contact_listbox.bind("<<ListboxSelect>>", self.switch_chat)

        self.right_frame = tk.Frame(master, bg="#2c2f33")
        self.right_frame.pack(side='right', fill='both', expand=True)

        self.chat_display = tk.Text(self.right_frame, state='disabled', bg="#2c2f33", fg="white")
        self.chat_display.pack(fill='both', expand=True, padx=10, pady=5)

        self.entry_frame = tk.Frame(self.right_frame, bg="#2c2f33")
        self.entry_frame.pack(fill='x', pady=(0, 10))

        self.msg_entry = tk.Entry(self.entry_frame)
        self.msg_entry.pack(side='left', fill='x', expand=True, padx=(10, 5))
        self.msg_entry.bind("<Return>", self.send_message)

        self.send_btn = tk.Button(self.entry_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side='right', padx=(0, 10))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server()

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def connect_to_server(self, host='localhost', port=5555):
        self.sock.connect((host, port))
        self.sock.send(self.username.encode())
        self.ensure_contact("everyone")
        self.display_message("everyone", "Connected to server.")

    def receive_messages(self):
        while True:
            try:
                msg = self.sock.recv(1024).decode()
                if msg.startswith("SYSTEM:USERLIST:"):
                    users = msg.replace("SYSTEM:USERLIST:", "").split(",")
                    for user in users:
                        if user != self.username:
                            self.ensure_contact(user)
                elif msg.startswith("(Private) "):
                    sender = msg.split()[1].split(":")[0]
                    self.display_message(sender, msg)
                else:
                    sender = msg.split(":")[0]
                    self.display_message("everyone", msg)
            except:
                break

    def ensure_contact(self, username):
        if username not in self.chat_logs:
            self.chat_logs[username] = []
            self.contact_listbox.insert(tk.END, username)

    def switch_chat(self, event):
        selection = self.contact_listbox.curselection()
        if selection:
            index = selection[0]
            self.active_chat = self.contact_listbox.get(index)
            self.refresh_chat_display()

    def refresh_chat_display(self):
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        for line in self.chat_logs.get(self.active_chat, []):
            self.chat_display.insert(tk.END, line + '\n')
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def send_message(self, event=None):
        msg = self.msg_entry.get()
        if msg.strip():
            target = self.active_chat
            if target != "everyone":
                payload = f"TO:{target}:{msg}"
                display = f"You (to {target}): {msg}"
            else:
                payload = msg
                display = f"You: {msg}"
            self.sock.send(payload.encode())
            self.display_message(target, display)
            self.msg_entry.delete(0, tk.END)

    def display_message(self, target, msg):
        self.ensure_contact(target)
        self.chat_logs[target].append(msg)
        if self.active_chat == target:
            self.refresh_chat_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()