CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS usuarios (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo_registro VARCHAR(6) UNIQUE NOT NULL,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dispositivo_id VARCHAR(120) UNIQUE,
    nombre VARCHAR(120),
    email VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS interacciones (
    id BIGSERIAL PRIMARY KEY,
    usuario_uuid UUID NOT NULL REFERENCES usuarios(uuid) ON DELETE CASCADE,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    origen VARCHAR(20) NOT NULL,
    texto_usuario TEXT NOT NULL,
    texto_respuesta TEXT NOT NULL,
    variables_extraidas JSONB NOT NULL DEFAULT '{}'::jsonb,
    sintomas_madre TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    sintomas_bebe TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    nivel_alerta VARCHAR(20),
    puntuacion_riesgo DOUBLE PRECISION,
    recomendaciones TEXT,
    fuente VARCHAR(80),
    reglas_activadas JSONB NOT NULL DEFAULT '[]'::jsonb,
    requiere_accion_inmediata BOOLEAN NOT NULL DEFAULT FALSE,
    feedback_util BOOLEAN,
    CONSTRAINT interacciones_origen_check CHECK (origen IN ('chat', 'voz', 'sistema'))
);

CREATE INDEX IF NOT EXISTS idx_usuarios_codigo_registro ON usuarios (codigo_registro);
CREATE INDEX IF NOT EXISTS idx_usuarios_dispositivo_id ON usuarios (dispositivo_id);
CREATE INDEX IF NOT EXISTS idx_interacciones_usuario_fecha ON interacciones (usuario_uuid, fecha DESC);
CREATE INDEX IF NOT EXISTS idx_interacciones_nivel_alerta ON interacciones (nivel_alerta);

INSERT INTO usuarios (codigo_registro, dispositivo_id, nombre, email, fecha_registro)
VALUES ('123456', 'device-demo-001', 'Usuario Demo', 'demo@neocare.local', CURRENT_TIMESTAMP)
ON CONFLICT (codigo_registro) DO UPDATE
SET dispositivo_id = EXCLUDED.dispositivo_id,
    fecha_registro = CURRENT_TIMESTAMP;