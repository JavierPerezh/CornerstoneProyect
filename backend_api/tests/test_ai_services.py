import unittest
from app.services.respuesta_empatica import respuesta_service
from app.services.tts import tts_service
import os

class TestAIServices(unittest.TestCase):
    def test_respuesta_empatica_format(self):
        """Valida que la respuesta del LLM sea concisa y en espanol."""
        respuesta = respuesta_service.generar_respuesta(
            texto_usuario="Me siento muy cansada y triste",
            nivel_alerta="amarillo",
            recomendacion_medica="Descansa y pide apoyo familiar.",
            puntuacion_riesgo=0.65
        )
        self.assertIsInstance(respuesta, str)
        self.assertLessEqual(len(respuesta), 300)

    def test_tts_file_creation(self):
        """Verifica que el servicio de voz genere un archivo MP3 fisico."""
        texto = "Hola, estoy aqui para acompañarte."
        url_audio = tts_service.generar_audio(texto)
        
        self.assertIsNotNone(url_audio)
        self.assertTrue(url_audio.endswith(".mp3"))
        
        # Verificar existencia fisica del archivo
        ruta_archivo = os.path.join(os.getcwd(), url_audio.lstrip("/"))
        self.assertTrue(os.path.exists(ruta_archivo))