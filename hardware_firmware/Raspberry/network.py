import socket

HOST = "0.0.0.0"
PORT = 5000

def receive_text():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)

    conn, addr = s.accept()
    data = conn.recv(1024).decode()
    conn.close()
    s.close()

    return data

def send_audio(data):
    s = socket.socket()
    s.connect((HOST, PORT))
    s.sendall(data)
    s.close()