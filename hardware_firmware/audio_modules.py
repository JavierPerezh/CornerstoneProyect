"""
audio_capture.py & audio_playback.py - Módulos de Audio

Captura: Grabación desde micrófono I2S (INMP441)
Reproducción: Salida por DAC I2S (PCM5102A)
"""

import pyaudio
import soundfile as sf
import numpy as np
import threading
import time
import os
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================================
# AUDIO CAPTURE
# ============================================================================

class AudioCapture:
    """
    Captura audio desde micrófono I2S.
    
    Características:
    - Grabación en formato WAV (PCM 16-bit)
    - Control de duración máxima
    - Buffer configurable
    - Detección de silencio (opcional)
    """
    
    def __init__(self, config: dict):
        """
        Inicializa captura de audio.
        
        Args:
            config: Diccionario con:
                - sample_rate: Frecuencia de muestreo (Hz)
                - channels: Número de canales (1=mono, 2=estéreo)
                - chunk_size: Tamaño del buffer
                - audio_format: Formato de audio (16-bit por defecto)
        """
        self.sample_rate = config.get('sample_rate', 16000)
        self.channels = config.get('channels', 1)
        self.chunk_size = config.get('chunk_size', 1024)
        self.audio_format = pyaudio.paInt16
        
        self.pyaudio = pyaudio.PyAudio()
        
        # Estado de grabación
        self._recording = False
        self._stream = None
        self._frames = []
        self._recording_thread = None
        
        logger.info(f"AudioCapture initialized: {self.sample_rate}Hz, " +
                   f"{self.channels} canal(es), chunk={self.chunk_size}")
    
    def start_recording(self, max_duration: int = 60) -> Optional[str]:
        """
        Inicia grabación de audio.
        
        Args:
            max_duration: Duración máxima en segundos
            
        Returns:
            Nombre del archivo guardado, o None si error
        """
        if self._recording:
            logger.warning("Ya hay una grabación en progreso")
            return None
        
        try:
            self._recording = True
            self._frames = []
            
            # Abrir stream de entrada
            self._stream = self.pyaudio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=None  # Usar dispositivo por defecto
            )
            
            logger.info(f"Grabación iniciada (max {max_duration}s)")
            
            # Thread de captura
            def record_thread():
                start_time = time.time()
                
                while self._recording:
                    # Verificar timeout
                    elapsed = time.time() - start_time
                    if elapsed > max_duration:
                        logger.warning(f"Timeout de grabación alcanzado ({elapsed:.1f}s)")
                        break
                    
                    try:
                        # Leer chunk de stream
                        data = self._stream.read(self.chunk_size, exception_on_overflow=False)
                        self._frames.append(data)
                    except Exception as e:
                        logger.error(f"Error leyendo stream de audio: {e}")
                        break
            
            self._recording_thread = threading.Thread(target=record_thread, daemon=True)
            self._recording_thread.start()
            
            return "recording..."  # Indica que está grabando
            
        except Exception as e:
            logger.error(f"Error iniciando grabación: {e}")
            self._recording = False
            return None
    
    def stop_recording(self) -> Optional[str]:
        """
        Detiene grabación y guarda archivo WAV.
        
        Returns:
            Ruta del archivo guardado, o None si error
        """
        if not self._recording:
            logger.warning("No hay grabación en progreso")
            return None
        
        try:
            self._recording = False
            
            # Esperar a que termine el thread
            if self._recording_thread:
                self._recording_thread.join(timeout=2.0)
            
            # Cerrar stream
            if self._stream:
                self._stream.stop_stream()
                self._stream.close()
                self._stream = None
            
            # Convertir datos a numpy array
            if not self._frames:
                logger.warning("No hay datos de audio grabados")
                return None
            
            audio_data = b''.join(self._frames)
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Crear directorio de recordings
            recordings_dir = '/home/pi/hardware-firmware/recordings'
            os.makedirs(recordings_dir, exist_ok=True)
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(recordings_dir, f'recording_{timestamp}.wav')
            
            # Guardar WAV
            sf.write(filename, audio_array, self.sample_rate)
            
            file_size = os.path.getsize(filename)
            duration = len(audio_array) / self.sample_rate
            
            logger.info(f"Grabación guardada: {filename} " +
                       f"({duration:.1f}s, {file_size} bytes)")
            
            return filename
            
        except Exception as e:
            logger.error(f"Error guardando grabación: {e}")
            return None
    
    def is_recording(self) -> bool:
        """Retorna True si está grabando"""
        return self._recording
    
    def cleanup(self):
        """Limpia recursos de audio"""
        try:
            if self._recording:
                self.stop_recording()
            
            if self._stream:
                self._stream.close()
            
            self.pyaudio.terminate()
            logger.info("AudioCapture cleaned up")
        except Exception as e:
            logger.error(f"Error limpiando AudioCapture: {e}")


# ============================================================================
# AUDIO PLAYBACK
# ============================================================================

class AudioPlayback:
    """
    Reproducción de audio a través de DAC I2S.
    
    Características:
    - Reproducción de archivos WAV
    - Control de volumen
    - Streaming eficiente
    - Callbacks para eventos
    """
    
    def __init__(self, config: dict):
        """
        Inicializa reproducción de audio.
        
        Args:
            config: Diccionario con:
                - sample_rate: Frecuencia de muestreo esperada
                - channels: Número de canales
                - chunk_size: Tamaño del buffer para reproducción
        """
        self.sample_rate = config.get('sample_rate', 16000)
        self.channels = config.get('channels', 1)
        self.chunk_size = config.get('chunk_size', 1024)
        self.audio_format = pyaudio.paInt16
        
        self.pyaudio = pyaudio.PyAudio()
        
        # Estado de reproducción
        self._playing = False
        self._stream = None
        self._playback_thread = None
        self._volume = 1.0  # 0.0 - 1.0
        
        logger.info(f"AudioPlayback initialized: {self.sample_rate}Hz, " +
                   f"{self.channels} canal(es)")
    
    def set_volume(self, volume: float):
        """
        Ajusta volumen de reproducción.
        
        Args:
            volume: Volumen 0.0 (silencio) a 1.0 (máximo)
        """
        self._volume = max(0.0, min(1.0, volume))
        logger.debug(f"Volumen establecido a {self._volume:.1%}")
    
    def play(self, filename: str) -> bool:
        """
        Reproduce un archivo de audio.
        
        Args:
            filename: Ruta del archivo WAV
            
        Returns:
            True si la reproducción se completó, False si error
        """
        if self._playing:
            logger.warning("Ya hay una reproducción en progreso")
            return False
        
        if not os.path.exists(filename):
            logger.error(f"Archivo no encontrado: {filename}")
            return False
        
        try:
            # Leer archivo de audio
            audio_data, sample_rate = sf.read(filename, dtype='int16')
            
            # Validar compatibilidad
            if sample_rate != self.sample_rate:
                logger.warning(f"Mismatch de sample rate: archivo={sample_rate}Hz, " +
                              f"esperado={self.sample_rate}Hz")
                # Intentar resamplear si es necesario
                audio_data = self._resample(audio_data, sample_rate, self.sample_rate)
            
            # Si es estéreo pero esperamos mono, convertir
            if len(audio_data.shape) > 1 and self.channels == 1:
                audio_data = audio_data.mean(axis=1).astype('int16')
            
            self._playing = True
            
            logger.info(f"Iniciando reproducción: {filename} " +
                       f"({len(audio_data) / sample_rate:.1f}s)")
            
            # Thread de reproducción
            def playback_thread():
                try:
                    # Abrir stream de salida
                    stream = self.pyaudio.open(
                        format=self.audio_format,
                        channels=self.channels,
                        rate=self.sample_rate,
                        output=True,
                        frames_per_buffer=self.chunk_size
                    )
                    
                    # Reproducir en chunks
                    for i in range(0, len(audio_data), self.chunk_size):
                        if not self._playing:
                            break
                        
                        chunk = audio_data[i:i+self.chunk_size]
                        
                        # Aplicar volumen
                        if self._volume < 1.0:
                            chunk = (chunk * self._volume).astype('int16')
                        
                        # Enviar a stream
                        stream.write(chunk.tobytes())
                    
                    stream.stop_stream()
                    stream.close()
                    
                except Exception as e:
                    logger.error(f"Error durante reproducción: {e}")
                
                finally:
                    self._playing = False
            
            self._playback_thread = threading.Thread(target=playback_thread, daemon=True)
            self._playback_thread.start()
            
            # Esperar a que termine
            if self._playback_thread:
                self._playback_thread.join()
            
            logger.info("Reproducción completada")
            return True
            
        except Exception as e:
            logger.error(f"Error reproduciendo archivo: {e}")
            self._playing = False
            return False
    
    def _resample(self, audio_data: np.ndarray, 
                  orig_sr: int, target_sr: int) -> np.ndarray:
        """
        Resamplea audio a una frecuencia diferente.
        
        Args:
            audio_data: Array de audio
            orig_sr: Sample rate original
            target_sr: Sample rate objetivo
            
        Returns:
            Audio remuestreado
        """
        try:
            import scipy.signal as sig
            
            # Calcular razón de remuestreo
            num_samples = int(len(audio_data) * target_sr / orig_sr)
            
            # Resamplear
            resampled = sig.resample(audio_data, num_samples)
            
            return resampled.astype('int16')
        except ImportError:
            logger.error("scipy no disponible para remuestreo")
            return audio_data
    
    def stop(self):
        """Detiene la reproducción"""
        self._playing = False
        logger.info("Reproducción detenida")
    
    def is_playing(self) -> bool:
        """Retorna True si está reproduciendo"""
        return self._playing
    
    def cleanup(self):
        """Limpia recursos de audio"""
        try:
            self.stop()
            self.pyaudio.terminate()
            logger.info("AudioPlayback cleaned up")
        except Exception as e:
            logger.error(f"Error limpiando AudioPlayback: {e}")


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """Test de audio"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    config = {
        'sample_rate': 16000,
        'channels': 1,
        'chunk_size': 1024
    }
    
    print("\n=== Test de Audio ===\n")
    
    # Test grabación
    print("Inicializando captura de audio...")
    capture = AudioCapture(config)
    
    print("Grabando 5 segundos (habla en el micrófono)...")
    capture.start_recording(max_duration=5)
    time.sleep(6)  # Esperar a que termine
    
    recording_file = capture.stop_recording()
    
    if recording_file:
        print(f"Grabación guardada: {recording_file}")
        
        # Test reproducción
        print("\nReproduciendo grabación...")
        playback = AudioPlayback(config)
        playback.play(recording_file)
        
        playback.cleanup()
    
    capture.cleanup()
    
    print("\n=== Test completado ===\n")
