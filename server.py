import socket, threading
from DiffieHellman import DiffieHellman, key_to_string
from vigenere import Vigenere

clients = {}
PRIME = 23
BASE = 5

def handle_client(conn, addr):
    print(f"[+] Connected by {addr}")

    # Step 1: Diffie-Hellman Key Exchange
    dh = DiffieHellman(PRIME, BASE)
    client_pubkey = int(conn.recv(1024).decode())
    conn.send(str(dh.pubKey).encode())

    shared_secret = dh.calcSharedSecret(client_pubkey)
    key = key_to_string(shared_secret)
    clients[conn] = key

    print(f"[DH] Shared secret with {addr}: {shared_secret}")
    print(f"[DH] Vigenere key for {addr}: {key}\n")

    try:
        while True:
            encrypted = conn.recv(1024).decode()
            if not encrypted:
                break
            msg = Vigenere.vigenere_decrypt(encrypted, key)

            print(f"[RECEIVED from {addr}] Encrypted: {encrypted}")
            print(f"[DECRYPTED for {addr}] Plaintext: {msg}\n")

            # Broadcast to other clients
            for client, k in clients.items():
                if client != conn:
                    re_encrypted = Vigenere.vigenere_encrypt(f"{addr}: {msg}", k)
                    print(f"[SENT to {client.getpeername()}] Re-encrypted: {re_encrypted}\n")
                    client.send(re_encrypted.encode())
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        print(f"[-] Disconnected: {addr}")
        clients.pop(conn)
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
