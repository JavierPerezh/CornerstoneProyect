import sounddevice as sd
import numpy as np

FS = 16000
DURATION = 3

def record_audio():
    audio = sd.rec(int(FS * DURATION), samplerate=FS, channels=1, dtype='float32')
    sd.wait()
    return audio.tobytes()