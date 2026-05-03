// constants/config.ts
// Solo rutas relativas, la IP se obtiene de services/config.ts

export const ENDPOINTS = {
  login: '/api/v1/auth/register',
  voz: '/api/v1/voz',
  vozStatus: '/api/v1/voz/status',
  historial: '/api/v1/historial',
  progreso: '/api/v1/progreso',
};

export const POLL_INTERVAL_MS = 2_000;
export const POLL_TIMEOUT_MS = 60_000;
