-- 003_add_views.sql
CREATE MATERIALIZED VIEW IF NOT EXISTS resumen_diario AS
SELECT
    usuario_uuid,
    DATE_TRUNC('day', fecha) AS dia,
    COUNT(*) AS total_interacciones,
    COUNT(*) FILTER (WHERE nivel_alerta = 'verde') AS alertas_verdes,
    COUNT(*) FILTER (WHERE nivel_alerta = 'amarillo') AS alertas_amarillas,
    COUNT(*) FILTER (WHERE nivel_alerta = 'rojo') AS alertas_rojas,
    ROUND(AVG(puntuacion_riesgo)::numeric, 3) AS riesgo_promedio,
    COUNT(*) FILTER (WHERE requiere_accion_inmediata = TRUE) AS acciones_inmediatas
FROM interacciones
GROUP BY usuario_uuid, DATE_TRUNC('day', fecha);

CREATE UNIQUE INDEX ON resumen_diario(usuario_uuid, dia);
