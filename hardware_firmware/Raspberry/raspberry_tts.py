import socket
import os

HOST = "0.0.0.0"
PORT = 5001

VOICE = "es-CO-SalomeNeural"

def speak(text):
    cmd = (
        f'edge-tts --voice {VOICE} '
        f'--text "{text}" '
        f'--write-media voz.mp3'
    )
    os.system(cmd)
    os.system("mpg123 voz.mp3 > /dev/null 2>&1")

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)

print("Servidor TTS listo...")

while True:
    conn, addr = s.accept()
    text = conn.recv(1024).decode()

    if text:
        print("Texto recibido:", text)
        speak(text)

    conn.close()