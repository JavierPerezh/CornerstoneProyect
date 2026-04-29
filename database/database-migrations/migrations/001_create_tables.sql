-- 001_create_tables.sql
-- Habilitar extensión UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Limpiar si existe
DROP TABLE IF EXISTS interacciones CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP MATERIALIZED VIEW IF EXISTS resumen_diario CASCADE;

-- Tabla usuarios
CREATE TABLE usuarios (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dispositivo_id VARCHAR(50) UNIQUE,
    codigo_registro VARCHAR(6),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    baby_birthdate DATE,
    fecha_registro TIMESTAMP DEFAULT NOW(),
    fecha_consentimiento TIMESTAMP,
    anonimizado BOOLEAN DEFAULT FALSE,
    fecha_anonimizacion TIMESTAMP
);

-- Tabla interacciones
CREATE TABLE interacciones (
    id SERIAL PRIMARY KEY,
    usuario_uuid UUID NOT NULL REFERENCES usuarios(uuid) ON DELETE CASCADE,
    fecha TIMESTAMP DEFAULT NOW(),
    origen VARCHAR(10) CHECK (origen IN ('voz', 'texto')),
    texto_usuario TEXT NOT NULL,
    texto_respuesta TEXT NOT NULL,
    variables_extraidas JSONB,
    sintomas_madre TEXT[],
    sintomas_bebe TEXT[],
    nivel_alerta VARCHAR(10) CHECK (nivel_alerta IN ('verde', 'amarillo', 'rojo')),
    puntuacion_riesgo FLOAT CHECK (puntuacion_riesgo >= 0 AND puntuacion_riesgo <= 1),
    recomendaciones TEXT,
    fuente TEXT,
    reglas_activadas TEXT[],
    requiere_accion_inmediata BOOLEAN DEFAULT FALSE,
    feedback_util BOOLEAN
);
