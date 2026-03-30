import os
import time
from pathlib import Path
from app.core.config import settings

class CleanupService:
    """
    Servicio de mantenimiento encargado de la depuracion automatica de 
    archivos de audio temporales para optimizar el almacenamiento.
    """

    def __init__(self):
        # Referencia al directorio estatico definido en la configuracion central
        self.audio_dir = settings.BASE_DIR / "static" / "audio"
        self.dias_retencion = 7
        self.max_archivos = 1000

    def ejecutar_limpieza(self):
        """
        Realiza una limpieza basada en la antiguedad de los archivos y 
        en la cuota maxima de almacenamiento definida.
        """
        if not self.audio_dir.exists():
            return

        print(f"--- Iniciando tareas de limpieza en: {self.audio_dir} ---")
        
        ahora = time.time()
        segundos_retencion = self.dias_retencion * 86400
        
        # 1. Obtener lista de archivos con sus metadatos de tiempo
        archivos = []
        for archivo in self.audio_dir.glob("*.mp3"):
            stats = archivo.stat()
            archivos.append({
                "path": archivo,
                "mtime": stats.st_mtime
            })

        # 2. Eliminacion por antiguedad (Mas de 7 dias)
        eliminados_por_fecha = 0
        for item in archivos:
            if ahora - item["mtime"] > segundos_retencion:
                try:
                    item["path"].unlink()
                    eliminados_por_fecha += 1
                except Exception as e:
                    print(f"Error al eliminar {item['path'].name}: {e}")

        # 3. Control de cuota maxima (Si exceden los 1000 archivos)
        # Se actualiza la lista tras la primera limpieza
        archivos_restantes = sorted(
            [f for f in self.audio_dir.glob("*.mp3")],
            key=os.path.getmtime
        )

        eliminados_por_cuota = 0
        if len(archivos_restantes) > self.max_archivos:
            exceso = len(archivos_restantes) - self.max_archivos
            for i in range(exceso):
                try:
                    archivos_restantes[i].unlink()
                    eliminados_por_cuota += 1
                except Exception as e:
                    print(f"Error al eliminar por cuota: {e}")

        print(f"Limpieza finalizada.")
        print(f"- Archivos eliminados por antiguedad: {eliminados_por_fecha}")
        print(f"- Archivos eliminados por cuota: {eliminados_por_cuota}")

# Instancia para ejecucion programada
cleanup_service = CleanupService()