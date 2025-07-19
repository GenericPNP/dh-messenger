import socket, threading

clients = {}  # conn: {"name": username}
PORT = 5555

def broadcast_user_list():
    user_list = [info["name"] for info in clients.values()]
    msg = "SYSTEM:USERLIST:" + ",".join(user_list)
    for conn in clients:
        try:
            conn.send(msg.encode())
        except:
            continue

def handle_client(conn, addr):
    try:
        name = conn.recv(1024).decode()
        clients[conn] = {"name": name}
        print(f"[+] {name} connected from {addr}")

        broadcast_user_list()

        while True:
            msg = conn.recv(1024).decode()
            if not msg:
                break

            if msg.startswith("TO:"):
                parts = msg.split(":", 2)
                if len(parts) == 3:
                    _, recipient, body = parts
                    for client, info in clients.items():
                        if info["name"] == recipient:
                            client.send(f"(Private) {name}: {body}".encode())
                            break
                    else:
                        conn.send("Server: Recipient not found.".encode())
            else:
                for client in clients:
                    if client != conn:
                        client.send(f"{name}: {msg}".encode())

    except Exception as e:
        print(f"[!] Error with {addr}: {e}")
    finally:
        print(f"[-] {clients[conn]['name']} disconnected")
        clients.pop(conn)
        broadcast_user_list()
        conn.close()

def start_server(host='localhost', port=PORT):
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