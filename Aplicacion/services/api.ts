// services/api.ts
// Tipos basados en el esquema real de init.sql (tabla interacciones)
import { ENDPOINTS, POLL_INTERVAL_MS, POLL_TIMEOUT_MS } from "../constants/config";
import { getToken, getDeviceId } from "./auth";
import { getServerUrl } from './config';
// Helper para construir URL absoluta
async function apiUrl(path: string): Promise<string> {
  const base = await getServerUrl();
  return `${base}${path}`;
}

// ── TIPOS ─────────────────────────────────────────────────────────────────────

/** Respuesta de POST /voz → task inmediata */
export interface VozTaskResponse {
  task_id: string;
  status: "procesando" | "completado" | "error";
  audio_url?: string;
  texto_respuesta?: string;
}

/** Fila de la tabla `interacciones` (historial) */
export interface Interaccion {
  id: number;
  fecha: string;                        // TIMESTAMP
  origen: "chat" | "voz" | "sistema";
  texto_usuario: string;
  texto_respuesta: string;
  nivel_alerta: "verde" | "amarillo" | "rojo" | null;
  puntuacion_riesgo: number | null;     // DOUBLE PRECISION del modelo ML
  recomendaciones: string | null;
  sintomas_madre: string[];             // TEXT[]
  sintomas_bebe: string[];              // TEXT[]
  requiere_accion_inmediata: boolean;
  feedback_util: boolean | null;
}

// ── HELPERS ───────────────────────────────────────────────────────────────────

async function deviceHeaders(): Promise<HeadersInit> {
  const deviceId = await getDeviceId();
  if (!deviceId) {
    throw new Error(
      "Dispositivo no configurado.\nVe a Ajustes e ingresa tu dispositivo_id."
    );
  }
  return { "X-Device-Id": deviceId };
}

async function authHeaders(): Promise<HeadersInit> {
  const token = await getToken();
  if (!token) throw new Error("Sesión expirada. Inicia sesión nuevamente.");
  return { Authorization: `Bearer ${token}` };
}

// ── VOZ: PASO 1 — Enviar audio WAV ────────────────────────────────────────────

async function enviarAudio(audioUri: string): Promise<string> {
  const headers = await deviceHeaders();

  const formData = new FormData();
  formData.append("audio", {
    uri: audioUri,
    name: "grabacion.wav",
    type: "audio/wav",  // ← voz.py solo acepta audio/wav o audio/x-wav
  } as any);

  const url = await apiUrl(ENDPOINTS.voz);
  const res = await fetch(url, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail || `Error ${res.status} al enviar audio`);
  }

  const data: VozTaskResponse = await res.json();
  return data.task_id;
}

// ── VOZ: PASO 2 — Polling ─────────────────────────────────────────────────────

async function esperarResultado(taskId: string): Promise<VozTaskResponse> {
  const headers = await deviceHeaders();
  // Construimos la URL absoluta una sola vez
  const baseUrl = await apiUrl(ENDPOINTS.vozStatus);
  const url = `${baseUrl}/${taskId}`;
  const deadline = Date.now() + POLL_TIMEOUT_MS;

  while (Date.now() < deadline) {
    const res = await fetch(url, { headers });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err?.detail || `Error ${res.status} consultando tarea`);
    }

    const data: VozTaskResponse = await res.json();
    if (data.status === "completado") return data;
    if (data.status === "error")
      throw new Error("El servidor reportó un error procesando el audio");

    await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
  }

  throw new Error("Tiempo de espera agotado. Intenta con un mensaje más corto.");
}

// ── VOZ: función pública ──────────────────────────────────────────────────────

export async function procesarVoz(audioUri: string): Promise<VozTaskResponse> {
  const taskId = await enviarAudio(audioUri);
  return esperarResultado(taskId);
}

export async function resolverUrlAudio(path: string): Promise<string> {
  if (path.startsWith('http')) return path;
  const base = await getServerUrl();
  return `${base}/${path.replace(/^\//, '')}`;
}

// ── HISTORIAL (tabla interacciones) ───────────────────────────────────────────

export async function obtenerHistorial(): Promise<Interaccion[]> {
  const headers = await authHeaders();
  const url = await apiUrl(ENDPOINTS.historial);
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error("No se pudo obtener el historial");
  return res.json();
}
