// services/auth.ts
import { getServerUrl } from './config';
import AsyncStorage from "@react-native-async-storage/async-storage";
import { ENDPOINTS } from "../constants/config";

const TOKEN_KEY      = "cornerst_jwt";
const UUID_KEY       = "cornerst_uuid";
const DEVICE_ID_KEY  = "cornerst_device_id";
const CODIGO_KEY     = "cornerst_codigo";

export interface AuthResponse {
  access_token: string;
  token_type: "bearer";
  usuario_uuid: string;
  dispositivo_id?: string;
}

// ── Login ──────────────────────────────────────────────────────
export async function login(codigo_registro: string): Promise<AuthResponse> {
  const baseUrl = await getServerUrl();
  const url = `${baseUrl}${ENDPOINTS.login}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ codigo_registro }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail || "Código de registro inválido");
  }

  const data: AuthResponse = await res.json();
  
  // Usamos AsyncStorage en lugar de SecureStore por compatibilidad con Expo Go
  await AsyncStorage.setItem(TOKEN_KEY, data.access_token);
  await AsyncStorage.setItem(UUID_KEY, data.usuario_uuid);
  await AsyncStorage.setItem(CODIGO_KEY, codigo_registro);

  if (data.dispositivo_id) {
    await AsyncStorage.setItem(DEVICE_ID_KEY, data.dispositivo_id);
  }

  return data;
}

// ── Device ID ──────────────────────────────────────────────────
export async function setDeviceId(deviceId: string): Promise<void> {
  await AsyncStorage.setItem(DEVICE_ID_KEY, deviceId);
}

export async function getDeviceId(): Promise<string | null> {
  return AsyncStorage.getItem(DEVICE_ID_KEY);
}

// ── Helpers ────────────────────────────────────────────────────
export async function getToken(): Promise<string | null> {
  return AsyncStorage.getItem(TOKEN_KEY);
}

export async function getCodigoRegistro(): Promise<string | null> {
  return AsyncStorage.getItem(CODIGO_KEY);
}

export async function logout(): Promise<void> {
  await AsyncStorage.multiRemove([TOKEN_KEY, UUID_KEY]);
  // Mantenemos DEVICE_ID y CODIGO para la siguiente sesión
}
