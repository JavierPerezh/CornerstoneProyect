// hooks/useVoiceSession.ts
import { useState, useRef, useCallback } from "react";
import { Audio } from "expo-av";
import { procesarVoz, resolverUrlAudio, VozTaskResponse } from "../services/api";

export type SessionStatus =
  | "idle"
  | "recording"
  | "sending"     // Subiendo audio al servidor
  | "processing"  // Polling: Whisper → Groq → Risk → Edge-TTS
  | "playing"
  | "error";

export const NIVEL_COLOR = {
  verde:    "#3db87a",
  amarillo: "#f0a500",
  rojo:     "#e05252",
};

// WAV 16kHz mono — formato exacto que acepta Whisper en el backend
const WAV_RECORDING_OPTIONS: Audio.RecordingOptions = {
  android: {
    extension: ".wav",
    outputFormat: Audio.AndroidOutputFormat.DEFAULT,
    audioEncoder: Audio.AndroidAudioEncoder.DEFAULT,
    sampleRate: 16000,
    numberOfChannels: 1,
    bitRate: 128000,
  },
  ios: {
    extension: ".wav",
    outputFormat: Audio.IOSOutputFormat.LINEARPCM,
    audioQuality: Audio.IOSAudioQuality.HIGH,
    sampleRate: 16000,
    numberOfChannels: 1,
    bitRate: 128000,
    linearPCMBitDepth: 16,
    linearPCMIsBigEndian: false,
    linearPCMIsFloat: false,
  },
  web: {},
};

export function useVoiceSession() {
  const [status, setStatus]     = useState<SessionStatus>("idle");
  const [response, setResponse] = useState<VozTaskResponse | null>(null);
  const [error, setError]       = useState<string | null>(null);

  const recordingRef = useRef<Audio.Recording | null>(null);
  const soundRef     = useRef<Audio.Sound | null>(null);

  // ── REPRODUCIR MP3 DE EDGE-TTS ────────────────────────────────────────────
  // Definida primero para poder usarla como dependencia de stopAndSend
  const reproducirAudio = useCallback(async (url: string) => {
    if (soundRef.current) {
      await soundRef.current.unloadAsync();
      soundRef.current = null;
    }

    await Audio.setAudioModeAsync({
      allowsRecordingIOS: false,
      playsInSilentModeIOS: true,
    });

    setStatus("playing");
    const { sound } = await Audio.Sound.createAsync({ uri: url });
    soundRef.current = sound;

    sound.setOnPlaybackStatusUpdate((s) => {
      if (s.isLoaded && s.didJustFinish) setStatus("idle");
    });

    await sound.playAsync();
  }, []); // sin deps — solo usa refs y setters estables

  // ── INICIAR GRABACIÓN ──────────────────────────────────────────────────────
  const startRecording = useCallback(async () => {
    try {
      setError(null);
      setResponse(null);

      const { granted } = await Audio.requestPermissionsAsync();
      if (!granted) throw new Error("Permiso de micrófono denegado");

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(WAV_RECORDING_OPTIONS);
      recordingRef.current = recording;
      setStatus("recording");
    } catch (e: any) {
      setError(e.message);
      setStatus("error");
    }
  }, []);

  // ── DETENER, ENVIAR Y HACER POLLING ───────────────────────────────────────
  const stopAndSend = useCallback(async () => {
    try {
      if (!recordingRef.current) return;
      setStatus("sending");

      await recordingRef.current.stopAndUnloadAsync();
      const uri = recordingRef.current.getURI();
      recordingRef.current = null;

      if (!uri) throw new Error("No se pudo obtener el archivo de audio");

      setStatus("processing");
      const result = await procesarVoz(uri);
      setResponse(result);

      if (result.audio_url) {
        await reproducirAudio(resolverUrlAudio(result.audio_url));
      } else {
        setStatus("idle");
      }
    } catch (e: any) {
      setError(e.message);
      setStatus("error");
    }
  }, [reproducirAudio]); // ← dep correcta

  const reset = useCallback(() => {
    setStatus("idle");
    setError(null);
    setResponse(null);
  }, []);

  return { status, response, error, startRecording, stopAndSend, reset };
}
