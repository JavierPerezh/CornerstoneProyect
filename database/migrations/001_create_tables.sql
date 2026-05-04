-- 001_create_tables.sql
-- Crea las 4 tablas principales del sistema posparto

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    uuid_anonimo VARCHAR(50) UNIQUE NOT NULL,
    nombre_anonimo VARCHAR(100),
    semanas_posparto INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS interacciones (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    mensaje_usuario TEXT NOT NULL,
    respuesta_bot TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alertas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    nivel VARCHAR(10) NOT NULL,
    motivo TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT ck_alerta_nivel CHECK (nivel IN ('verde', 'amarillo', 'rojo'))
);

CREATE TABLE IF NOT EXISTS progreso_diario (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha TIMESTAMP DEFAULT NOW(),
    estado_animo INTEGER NOT NULL,
    horas_sueno FLOAT,
    notas TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
