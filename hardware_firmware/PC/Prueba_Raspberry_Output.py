import socket

HOST = "192.168.80.25"
PORT = 5001

while True:
    text = input("Texto: ")

    s = socket.socket()
    s.connect((HOST, PORT))
    s.sendall(text.encode())
    s.close()
