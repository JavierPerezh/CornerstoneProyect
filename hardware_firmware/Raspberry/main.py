from audio_input import record_audio
from audio_output import play_audio
from network import send_audio, receive_text

def main():
    print("Asistente iniciado...")

    while True:
        try:
            # 1. Escuchar
            print("Escuchando...")
            audio = record_audio()

            # 2. Enviar a IA
            print("Enviando...")
            send_audio(audio)

            # 3. Recibir respuesta
            print("Recibiendo...")
            response = receive_text()

            # 4. Reproducir
            print("Hablando...")
            play_audio(response)

        except KeyboardInterrupt:
            print("Saliendo...")
            break

if __name__ == "__main__":
    main()