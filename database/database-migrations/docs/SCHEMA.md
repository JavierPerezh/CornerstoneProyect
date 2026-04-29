# Esquema de Base de Datos — Salud Posparto v2

Documentación del modelo de datos de la API de seguimiento posparto.

---

## 1. Modelo de datos

El sistema almacena interacciones anónimas entre usuarias y un asistente conversacional, con clasificación de riesgo automática (`verde`/`amarillo`/`rojo`). Las usuarias se identifican por un UUID anónimo asociado a un dispositivo.

Componentes principales:
- **`usuarios`**: identidad anónima por UUID + metadatos de consentimiento.
- **`interacciones`**: historial cronológico con clasificación de riesgo, síntomas extraídos y recomendaciones.
- **`resumen_diario`** (vista materializada): agregaciones por día/usuario para gráficos rápidos.

---

## 2. Diagrama de relaciones

```
┌──────────────────────────┐
│        usuarios          │
├──────────────────────────┤
│ uuid (PK)            UUID│
│ dispositivo_id   VARCHAR │
│ codigo_registro  VARCHAR │
│ fecha_registro  TIMESTAMP│
│ fecha_consentim TIMESTAMP│
│ anonimizado       BOOLEAN│
│ fecha_anonimiz  TIMESTAMP│
└────────────┬─────────────┘
             │ 1
             │
             │ N  (ON DELETE CASCADE)
┌────────────▼─────────────┐
│      interacciones       │
├──────────────────────────┤
│ id (PK)            SERIAL│
│ usuario_uuid (FK)    UUID│
│ fecha           TIMESTAMP│
│ origen           VARCHAR │  ← 'voz' | 'texto'
│ texto_usuario       TEXT │
│ texto_respuesta     TEXT │
│ variables_extraidas JSONB│
│ sintomas_madre    TEXT[] │
│ sintomas_bebe     TEXT[] │
│ nivel_alerta     VARCHAR │  ← 'verde' | 'amarillo' | 'rojo'
│ puntuacion_riesgo  FLOAT │  ← [0.0, 1.0]
│ recomendaciones     TEXT │
│ fuente              TEXT │
│ reglas_activadas  TEXT[] │
│ requiere_accion_inm BOOL │
│ feedback_util       BOOL │
└────────────┬─────────────┘
             │
             ▼
   ┌─────────────────────────────────┐
   │  resumen_diario (MAT. VIEW)     │
   ├─────────────────────────────────┤
   │ usuario_uuid, dia               │
   │ total_interacciones             │
   │ alertas_verdes/amarillas/rojas  │
   │ riesgo_promedio                 │
   │ acciones_inmediatas             │
   └─────────────────────────────────┘
```

---

## 3. Tablas

### 3.1 `usuarios`

| Columna | Tipo | Descripción |
|---|---|---|
| `uuid` | `UUID` PK | Identificador anónimo (generado con `gen_random_uuid()`) |
| `dispositivo_id` | `VARCHAR(50)` UNIQUE | ID del dispositivo físico que emparejó (opcional) |
| `codigo_registro` | `VARCHAR(6)` | Código corto para emparejar la app con el dispositivo |
| `fecha_registro` | `TIMESTAMP` | Fecha de creación del registro (default `NOW()`) |
| `fecha_consentimiento` | `TIMESTAMP` | Fecha en la que la usuaria aceptó el consentimiento informado |
| `anonimizado` | `BOOLEAN` | Indica si los datos fueron anonimizados (derecho al olvido) |
| `fecha_anonimizacion` | `TIMESTAMP` | Fecha en que se ejecutó la anonimización |

### 3.2 `interacciones`

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | `SERIAL` PK | Identificador autoincremental |
| `usuario_uuid` | `UUID` FK → `usuarios.uuid` | Usuaria propietaria. `ON DELETE CASCADE` |
| `fecha` | `TIMESTAMP` | Cuándo ocurrió la interacción (default `NOW()`) |
| `origen` | `VARCHAR(10)` | Canal: `'voz'` o `'texto'` (CHECK) |
| `texto_usuario` | `TEXT` | Lo que dijo/escribió la usuaria |
| `texto_respuesta` | `TEXT` | Respuesta del bot |
| `variables_extraidas` | `JSONB` | Variables clave detectadas por el NLU (estructura libre) |
| `sintomas_madre` | `TEXT[]` | Síntomas detectados en la madre |
| `sintomas_bebe` | `TEXT[]` | Síntomas detectados en el bebé |
| `nivel_alerta` | `VARCHAR(10)` | `'verde'` / `'amarillo'` / `'rojo'` (CHECK) |
| `puntuacion_riesgo` | `FLOAT` | Score `[0.0, 1.0]` (CHECK) |
| `recomendaciones` | `TEXT` | Texto plano con recomendaciones generadas |
| `fuente` | `TEXT` | Guía clínica o fuente de la recomendación |
| `reglas_activadas` | `TEXT[]` | Reglas del motor que se dispararon |
| `requiere_accion_inmediata` | `BOOLEAN` | Si `TRUE`, mostrar banner de urgencia |
| `feedback_util` | `BOOLEAN` | Feedback de la usuaria: ¿fue útil? (NULL = sin responder) |

---

## 4. Índices

| Índice | Columnas | Propósito |
|---|---|---|
| `idx_interacciones_usuario_fecha` | `(usuario_uuid, fecha DESC)` | Acelera el historial paginado por usuaria |
| `idx_interacciones_nivel` | `(nivel_alerta)` | Filtros y conteos por nivel |
| `idx_interacciones_riesgo` | `(puntuacion_riesgo)` | Búsquedas y promedios por score |
| `idx_interacciones_variables` | `GIN(variables_extraidas)` | Búsquedas en JSONB con operadores `@>`, `?` |

---

## 5. Vista materializada `resumen_diario`

Pre-agrega métricas por día y usuaria. Se refresca con:

```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY resumen_diario;
```

Columnas: `usuario_uuid`, `dia`, `total_interacciones`, `alertas_verdes`, `alertas_amarillas`, `alertas_rojas`, `riesgo_promedio`, `acciones_inmediatas`.

Tiene índice único en `(usuario_uuid, dia)` necesario para `REFRESH CONCURRENTLY`.

---

## 6. Consultas de ejemplo

### 6.1 Historial paginado de una usuaria

```sql
SELECT id, fecha, origen, texto_usuario, nivel_alerta, puntuacion_riesgo
FROM interacciones
WHERE usuario_uuid = 'a0000000-0000-0000-0000-000000000001'
ORDER BY fecha DESC
LIMIT 50 OFFSET 0;
```

### 6.2 Conteo de alertas por nivel (últimos 7 días)

```sql
SELECT nivel_alerta, COUNT(*) AS total
FROM interacciones
WHERE usuario_uuid = 'a0000000-0000-0000-0000-000000000001'
  AND fecha >= NOW() - INTERVAL '7 days'
GROUP BY nivel_alerta;
```

### 6.3 Top 5 síntomas más frecuentes

```sql
SELECT s AS sintoma, COUNT(*) AS frecuencia
FROM interacciones, UNNEST(sintomas_madre) AS s
WHERE usuario_uuid = 'a0000000-0000-0000-0000-000000000001'
GROUP BY s
ORDER BY frecuencia DESC
LIMIT 5;
```

### 6.4 Riesgo promedio por semana

```sql
SELECT DATE_TRUNC('week', fecha) AS semana,
       ROUND(AVG(puntuacion_riesgo)::numeric, 3) AS riesgo
FROM interacciones
WHERE usuario_uuid = 'a0000000-0000-0000-0000-000000000001'
GROUP BY semana
ORDER BY semana;
```

### 6.5 Interacciones que requieren acción inmediata

```sql
SELECT id, fecha, texto_usuario, recomendaciones
FROM interacciones
WHERE requiere_accion_inmediata = TRUE
ORDER BY fecha DESC;
```

---

## 7. UUIDs de prueba

Para desarrollo y testing existen 3 usuarias precargadas (ver migración `004_seed_test_data.sql`):

| UUID | Notas |
|---|---|
| `a0000000-0000-0000-0000-000000000001` | Usuaria con escalada hacia alerta roja al final |
| `a0000000-0000-0000-0000-000000000002` | Patrón mixto con énfasis en salud mental |
| `a0000000-0000-0000-0000-000000000003` | Buen estado inicial, deterioro progresivo |

Cada una tiene 20 interacciones distribuidas en los últimos 30 días con la siguiente proporción de alertas:
- 60 % verde (riesgo 0.0–0.3)
- 30 % amarillo (riesgo 0.3–0.7)
- 10 % rojo (riesgo 0.7–1.0)
