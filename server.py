import socket, threading
from DiffieHellman import DiffieHellman, key_to_string
from vigenere import Vigenere

clients = {}  # conn: {"key": shared_key, "name": username}
PRIME = 23
BASE = 5

def broadcast_user_list():
    user_list = [info["name"] for info in clients.values()]
    msg = "SYSTEM:USERLIST:" + ",".join(user_list)
    for client, info in clients.items():
        encrypted = Vigenere.vigenere_encrypt(msg, info["key"])
        try:
            client.send(encrypted.encode())
        except:
            continue

def handle_client(conn, addr):
    print(f"[+] Connected by {addr}")

    # Step 1: Diffie-Hellman Key Exchange
    dh = DiffieHellman(PRIME, BASE)
    client_pubkey = int(conn.recv(1024).decode())
    conn.send(str(dh.pubKey).encode())

    shared_secret = dh.calcSharedSecret(client_pubkey)
    key = key_to_string(shared_secret)

    # Step 2: Receive client name
    encrypted_name = conn.recv(1024).decode()
    name = Vigenere.vigenere_decrypt(encrypted_name, key)

    clients[conn] = {"key": key, "name": name}
    print(f"[DH] Shared secret with {addr} ({name}): {shared_secret}")
    print(f"[DH] Vigenere key for {addr} ({name}): {key}\n")

    broadcast_user_list()

    try:
        while True:
            encrypted = conn.recv(1024).decode()
            if not encrypted:
                break
            msg = Vigenere.vigenere_decrypt(encrypted, key)

            # Handle system/user list update messages
            if msg.startswith("TO:"):
                parts = msg.split(":", 2)
                if len(parts) == 3:
                    _, recipient_name, body = parts
                    sent = False
                    for client, info in clients.items():
                        if info["name"] == recipient_name:
                            encrypted_msg = Vigenere.vigenere_encrypt(f"(Private) {name}: {body}", info["key"])
                            client.send(encrypted_msg.encode())
                            sent = True
                    if not sent:
                        error_msg = Vigenere.vigenere_encrypt("Server: Recipient not found.", key)
                        conn.send(error_msg.encode())
                continue

            # Broadcast to all other clients
            for client, info in clients.items():
                if client != conn:
                    encrypted_msg = Vigenere.vigenere_encrypt(f"{name}: {msg}", info["key"])
                    client.send(encrypted_msg.encode())

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        print(f"[-] Disconnected: {addr} ({name})")
        clients.pop(conn)
        broadcast_user_list()
        conn.close()

def start_server(host='localhost', port=5555):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[*] Server listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
