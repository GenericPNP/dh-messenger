import socket, threading
from DiffieHellman import DiffieHellman, key_to_string
from vigenere import Vigenere

PRIME = 23
BASE = 5

def receive_messages(sock, key):
    while True:
        try:
            encrypted = sock.recv(1024).decode()
            if encrypted:
                msg = Vigenere.vigenere_decrypt(encrypted, key)
                print(msg)
        except:
            break

def start_client(host='localhost', port=5555):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # Step 1: Diffie-Hellman key exchange
    dh = DiffieHellman(PRIME, BASE)
    client.send(str(dh.pubKey).encode())
    server_pubkey = int(client.recv(1024).decode())
    shared_secret = dh.calcSharedSecret(server_pubkey)
    key = key_to_string(shared_secret)

    # Step 2: Start message receiving thread
    threading.Thread(target=receive_messages, args=(client, key), daemon=True).start()

    # Step 3: Send messages
    try:
        while True:
            msg = input()
            if msg.strip().lower() == 'exit':
                break
            encrypted = Vigenere.vigenere_encrypt(msg, key)
            client.send(encrypted.encode())
    except KeyboardInterrupt:
        pass
    finally:
        print("[-] Disconnected.")
        client.close()

if __name__ == "__main__":
    start_client()
