import os
import uuid
import asyncio
import edge_tts
from datetime import datetime
from app.core.config import settings
import nest_asyncio

# Permitir event loops anidados (necesario para Jupyter)
try:
    nest_asyncio.apply()
except RuntimeError:
    pass  # Ya fue aplicado

class TTSService:
    """
    Servicio de síntesis de voz utilizando Edge-TTS.
    No requiere API Keys y ofrece voces neuronales de alta calidad.
    """

    def __init__(self):
        # Usamos una voz femenina de México para un tono cálido y cercano
        self.voice = "es-MX-DaliaNeural" 

    async def generar_audio_async(self, texto):
        """
        Versión asíncrona de la síntesis de voz.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        identificador = str(uuid.uuid4())[:8]
        nombre_archivo = f"respuesta_{timestamp}_{identificador}.mp3"
        
        # Ruta de almacenamiento
        ruta_directorio = os.path.join("static", "audio")
        os.makedirs(ruta_directorio, exist_ok=True)
        ruta_completa = os.path.join(ruta_directorio, nombre_archivo)

        try:
            communicate = edge_tts.Communicate(texto, self.voice)
            await communicate.save(ruta_completa)
            return f"/static/audio/{nombre_archivo}"
        except Exception as e:
            print(f"Error en Edge-TTS: {e}")
            return None

    def generar_audio(self, texto):
        """
        Wrapper síncrono para mantener compatibilidad con tus tests actuales.
        """
        try:
            # Obtener el event loop actual o crear uno
            try:
                loop = asyncio.get_running_loop()
                # Si hay un loop ejecutándose, usar nest_asyncio
                return asyncio.run(self.generar_audio_async(texto))
            except RuntimeError:
                # No hay loop en ejecución, crear uno normal
                return asyncio.run(self.generar_audio_async(texto))
        except Exception as e:
            print(f"Error al ejecutar TTS síncrono: {e}")
            return None

# Instancia global
tts_service = TTSService()