# 📋 Formato de Datos - Modelo de Riesgo Posparto

## Descripción General

El modelo de **Regresión Logística Multinomial** utiliza **17 características numéricas** para evaluar el nivel de riesgo posparto (bajo, medio, alto). Todos los datos se **normalizan automáticamente** usando Z-score antes de ser procesados por el modelo.

---

## 📊 Variables del Modelo (17 características)

| # | Variable | Tipo | Rango | Media | Desv. Est. | Descripción |
|---|----------|------|-------|-------|------------|-------------|
| 1 | `dias_posparto` | int | 1-42 | 21.636 | 11.900 | Días transcurridos desde el parto |
| 2 | `horas_sueno` | float | 0-12 | 5.970 | 1.498 | Horas de sueño en las últimas 24h |
| 3 | `nivel_dolor` | int | 0-10 | 5.034 | 3.122 | Escala de dolor (0=sin dolor, 10=máximo) |
| 4 | `fiebre_madre` | float | 36.0-40.0 | 0.050 | 0.217 | Temperatura corporal de la madre (°C) o binario |
| 5 | `fiebre_bebe` | int | 0-1 | 0.044 | 0.205 | Presencia de fiebre en el recién nacido (1=sí, 0=no) |
| 6 | `sangrado_abundante` | int | 0-1 | 0.018 | 0.133 | Hemorragia postparto (1=sí, 0=no) |
| 7 | `estado_animo` | int | 0-5 | 3.008 | 1.387 | Escala de estado emocional (0=deprimido, 5=excelente) |
| 8 | `apoyo_social` | int | 0-1 | 0.802 | 0.398 | Disponibilidad de apoyo (1=sí, 0=no) |
| 9 | `dificultad_lactancia` | int | 0-1 | 0.294 | 0.455 | Problemas de lactancia (1=sí, 0=no) |
| 10 | `llanto_bebe` | int | 0-5 | 3.031 | 1.430 | Intensidad del llanto del bebé (0=tranquilo, 5=muy irritable) |
| 11 | `dolor_cabecera` | int | 0-10 | 2.515 | 1.717 | Intensidad de cefalea (0=sin dolor, 10=máximo) |
| 12 | `hinchazon_edema` | int | 0-1 | 0.103 | 0.303 | Edema en extremidades (1=sí, 0=no) |
| 13 | `nivel_ansiedad` | int | 0-10 | 3.052 | 1.425 | Escala de ansiedad (0=tranquila, 10=muy ansiosa) |
| 14 | `actividad_fisica` | int | 0-1 | 0.700 | 0.458 | Realizó actividad física (1=sí, 0=no) |
| 15 | `perdida_apetito` | int | 0-1 | 0.107 | 0.308 | Cambio de apetito (1=sí, 0=no) |
| 16 | `vinculo_bebe` | int | 1-5 | 3.513 | 1.109 | Calidad del vínculo con el bebé (1=débil, 5=excelente) |
| 17 | `tipo_parto` | int | 0-1 | 0.499 | 0.500 | Tipo de parto (0=vaginal, 1=cesárea) |

---

## 🔄 Orden de Entrada (IMPORTANTE)

**El modelo REQUIERE las variables en este ORDEN exacto:**

```python
feature_order = [
    "dias_posparto",
    "horas_sueno",
    "nivel_dolor",
    "fiebre_madre",
    "fiebre_bebe",
    "sangrado_abundante",
    "estado_animo",
    "apoyo_social",
    "dificultad_lactancia",
    "llanto_bebe",
    "dolor_cabecera",
    "hinchazon_edema",
    "nivel_ansiedad",
    "actividad_fisica",
    "perdida_apetito",
    "vinculo_bebe",
    "tipo_parto"
]
```

---

## 📥 Estructura de Entrada (Diccionario Python)

```python
datos_madre = {
    "dias_posparto": 5,              # int
    "horas_sueno": 7,                # float
    "nivel_dolor": 3,                # int (0-10)
    "fiebre_madre": 37.0,            # float (°C)
    "fiebre_bebe": 0,                # int (0 o 1)
    "sangrado_abundante": 1,         # int (0 o 1)
    "estado_animo": 3,               # int (0-5)
    "apoyo_social": 1,               # int (0 o 1)
    "dificultad_lactancia": 0,       # int (0 o 1)
    "llanto_bebe": 2,                # int (0-5)
    "dolor_cabecera": 2,             # int (0-10)
    "hinchazon_edema": 0,            # int (0 o 1)
    "nivel_ansiedad": 2,             # int (0-10)
    "actividad_fisica": 0,           # int (0 o 1)
    "perdida_apetito": 0,            # int (0 o 1)
    "vinculo_bebe": 4,               # int (1-5)
    "tipo_parto": 1                  # int (0 o 1)
}
```

---

## 📤 Estructura de Salida (Respuesta del Modelo)

```python
{
    "nivel_riesgo": "rojo|amarillo|verde",        # Nivel final de riesgo
    "recomendacion_base": "Texto con recomendación médica",
    "detalle_tecnico": {
        "metodo_decisivo": "Reglas Clínicas|Modelo IA",
        "alerta_reglas": "rojo|amarillo|verde",
        "alerta_ml": "rojo|amarillo|verde",
        "confianza_ml": 0.95                       # Probabilidad (0-1)
    }
}
```

---

## 🔬 Proceso de Normalización

Cada variable se normaliza usando **Z-score**:

$$z_i = \frac{x_i - \mu_i}{\sigma_i}$$

Donde:
- $x_i$ = valor de la variable
- $\mu_i$ = media de la variable (ver tabla)
- $\sigma_i$ = desviación estándar (ver tabla)

**Ejemplo:**
```
dias_posparto = 5
media = 21.636
desv_est = 11.900

z_normalized = (5 - 21.636) / 11.900 = -1.397
```

---

## 🎯 Clasificación Final

El modelo produce **3 clases**:

| Clase | Nivel | Acción Recomendada |
|-------|-------|-------------------|
| 0 | 🟢 **Verde** | Acompañamiento y prevención |
| 1 | 🟡 **Amarillo** | Seguimiento en 24 horas |
| 2 | 🔴 **Rojo** | Emergencia médica inmediata |

---

## ⚠️ Notas Importantes

1. **Variables Binarias**: `fiebre_bebe`, `sangrado_abundante`, `apoyo_social`, `dificultad_lactancia`, `hinchazon_edema`, `actividad_fisica`, `perdida_apetito`, `tipo_parto` deben ser **0 o 1**.

2. **Variables Ordinales**: `estado_animo` (0-5), `nivel_dolor` (0-10), `dolor_cabecera` (0-10), `llanto_bebe` (0-5), `nivel_ansiedad` (0-10), `vinculo_bebe` (1-5).

3. **Variables Continuas**: `horas_sueno` (0-12), `fiebre_madre` (36-40°C o normalizado).

4. **Arbitraje de Decisión**: Si el Motor de Reglas detecta "rojo", **SIEMPRE prevalece sobre el modelo ML** por seguridad clínica.

5. **Datos Faltantes**: Si una variable no está disponible, usar la **media** de la variable como valor por defecto (ver columna "Media" en la tabla).

---

## 📝 Ejemplo de Uso

```python
from app.services.risk_service import risk_service

# Crear diccionario con datos de la madre
datos = {
    "dias_posparto": 5,
    "horas_sueno": 7,
    "nivel_dolor": 3,
    "fiebre_madre": 37.0,
    "fiebre_bebe": 0,
    "sangrado_abundante": 1,  # ⚠️ ALERTA ROJA
    "estado_animo": 3,
    "apoyo_social": 1,
    "dificultad_lactancia": 0,
    "llanto_bebe": 2,
    "dolor_cabecera": 2,
    "hinchazon_edema": 0,
    "nivel_ansiedad": 2,
    "actividad_fisica": 0,
    "perdida_apetito": 0,
    "vinculo_bebe": 4,
    "tipo_parto": 1
}

# Procesar evaluación
resultado = risk_service.procesar_evaluacion_completa(datos)

print(f"Riesgo: {resultado['nivel_riesgo']}")
print(f"Recomendación: {resultado['recomendacion_base']}")
```

---

## 📚 Referencias

- **Fecha de Entrenamiento**: 21 de abril de 2026
- **Dataset**: `datos_madres.csv` (2000 registros sintéticos)
- **Algoritmo**: Regresión Logística Multinomial con descenso del gradiente
- **Validación**: In-sample precision registrada en el entrenamiento
- **Motor de Reglas**: 20 reglas clínicas basadas en OMS, ACOG, SEGO

---

**Versión**: 1.0.0 | **Última actualización**: 2026-04-21
