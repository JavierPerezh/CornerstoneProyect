import os

VOICE = "es-CO-SalomeNeural"

def play_audio(text):
    os.system(
        f'edge-tts --voice {VOICE} '
        f'--text "{text}" '
        f'--write-media voz.mp3'
    )
    os.system("mpg123 voz.mp3 > /dev/null 2>&1")