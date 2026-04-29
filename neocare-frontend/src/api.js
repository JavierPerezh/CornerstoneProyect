const API_BASE_URL = 'http://localhost:8000/api/v1';

const getAuthHeader = (token) => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`,
});

const handleResponse = async (response) => {
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(data?.detail || `HTTP ${response.status}`);
  }
  return data;
};

export const apiService = {
  // ─────────────────────────────────────────────────────────────────
  // AUTENTICACIÓN
  // ─────────────────────────────────────────────────────────────────
  register: async (email, password, nombre, babyBirthdate) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, nombre, baby_birthdate: babyBirthdate }),
    });
    return handleResponse(response);
  },

  login: async (email, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(response);
  },

  validateToken: async (token) => {
    const response = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      headers: getAuthHeader(token),
    });
    return handleResponse(response);
  },

  // ─────────────────────────────────────────────────────────────────
  // CHAT
  // ─────────────────────────────────────────────────────────────────
  sendMessage: async (mensaje, usuarioUuid, token) => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: getAuthHeader(token),
      body: JSON.stringify({ mensaje, usuario_uuid: usuarioUuid }),
    });
    return handleResponse(response);
  },

  sendFeedback: async (interaccionId, util, token) => {
    const response = await fetch(`${API_BASE_URL}/chat/feedback`, {
      method: 'POST',
      headers: getAuthHeader(token),
      body: JSON.stringify({ interaccion_id: interaccionId, util }),
    });
    return handleResponse(response);
  },

  // ─────────────────────────────────────────────────────────────────
  // HISTORIAL
  // ─────────────────────────────────────────────────────────────────
  getHistorial: async (usuarioUuid, token, { limit = 50, offset = 0 } = {}) => {
    const params = new URLSearchParams({
      usuario_uuid: usuarioUuid,
      limit,
      offset,
    });
    const response = await fetch(`${API_BASE_URL}/historial?${params}`, {
      method: 'GET',
      headers: getAuthHeader(token),
    });
    return handleResponse(response);
  },

  getInteraccion: async (interaccionId, token) => {
    const response = await fetch(`${API_BASE_URL}/historial/${interaccionId}`, {
      method: 'GET',
      headers: getAuthHeader(token),
    });
    return handleResponse(response);
  },

  // ─────────────────────────────────────────────────────────────────
  // PROGRESO Y ANALÍTICA
  // ─────────────────────────────────────────────────────────────────
  getProgresoResumen: async (usuarioUuid, token, periodo = 'semana') => {
    const params = new URLSearchParams({
      usuario_uuid: usuarioUuid,
      periodo,
    });
    const response = await fetch(`${API_BASE_URL}/progreso/resumen?${params}`, {
      method: 'GET',
      headers: getAuthHeader(token),
    });
    return handleResponse(response);
  },

  getProgresoGrafico: async (usuarioUuid, token, agrupacion = 'dia') => {
    const params = new URLSearchParams({
      usuario_uuid: usuarioUuid,
      agrupacion,
    });
    const response = await fetch(`${API_BASE_URL}/progreso/grafico?${params}`, {
      method: 'GET',
      headers: getAuthHeader(token),
    });
    return handleResponse(response);
  },

  // ─────────────────────────────────────────────────────────────────
  // VOZ
  // ─────────────────────────────────────────────────────────────────
  sendAudio: async (audioFile, deviceId) => {
    const formData = new FormData();
    formData.append('audio', audioFile);

    const response = await fetch(`${API_BASE_URL}/voz`, {
      method: 'POST',
      headers: { 'X-Device-Id': deviceId },
      body: formData,
    });
    return handleResponse(response);
  },

  getAudioStatus: async (taskId, deviceId) => {
    const response = await fetch(`${API_BASE_URL}/voz/status/${taskId}`, {
      method: 'GET',
      headers: { 'X-Device-Id': deviceId },
    });
    return handleResponse(response);
  },

  // ─────────────────────────────────────────────────────────────────
  // HEALTH
  // ─────────────────────────────────────────────────────────────────
  health: async () => {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    return handleResponse(response);
  },
};