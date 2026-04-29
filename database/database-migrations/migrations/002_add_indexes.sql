-- 002_add_indexes.sql
CREATE INDEX idx_interacciones_usuario_fecha ON interacciones(usuario_uuid, fecha DESC);
CREATE INDEX idx_interacciones_nivel ON interacciones(nivel_alerta);
CREATE INDEX idx_interacciones_riesgo ON interacciones(puntuacion_riesgo);
CREATE INDEX idx_interacciones_variables ON interacciones USING GIN (variables_extraidas);
