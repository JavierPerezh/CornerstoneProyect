"""
Inserta datos sintéticos: 3 usuarios fijos + 60 interacciones (20 por usuario).
Distribución: 60% verde, 30% amarillo, 10% rojo.
Uso: python database-migrations/scripts/seed_data.py
"""

import os
import random
import sys
import uuid as uuid_lib
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = ROOT / "backend_api" / ".env"

load_dotenv(ENV_PATH)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print(f"❌ DATABASE_URL no encontrada en {ENV_PATH}")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

USUARIOS_FIJOS = [
    "a0000000-0000-0000-0000-000000000001",
    "a0000000-0000-0000-0000-000000000002",
    "a0000000-0000-0000-0000-000000000003",
]

SINTOMAS_MADRE = ["fatiga", "dolor de cabeza", "tristeza", "insomnio", "fiebre", "dolor pecho"]
SINTOMAS_BEBE = ["llanto excesivo", "fiebre", "no come", "vomito", "ictericia"]

PLANTILLAS_VERDE = [
    ("Hoy me siento bien", "Me alegra escucharte. ¿Cómo está el bebé?"),
    ("Dormí bien anoche", "Eso es muy importante para tu recuperación."),
    ("El bebé come bien", "Perfecto, sigue así."),
    ("Salí a caminar", "Excelente, el ejercicio suave ayuda."),
    ("Me siento tranquila", "Me alegra mucho."),
]
PLANTILLAS_AMARILLO = [
    ("Tengo fatiga constante", "Cuida tu hidratación y descanso."),
    ("Me siento triste", "Considera hablar con un profesional."),
    ("No puedo dormir bien", "Si persiste, consulta médicamente."),
    ("El bebé llora mucho", "Vigila hambre, sueño y temperatura."),
    ("Dolor de cabeza moderado", "Hidratación y descanso."),
]
PLANTILLAS_ROJO = [
    ("Tengo fiebre muy alta", "Acude a urgencias de inmediato."),
    ("Dolor fuerte en el pecho", "Esto requiere atención médica urgente."),
    ("El bebé tiene fiebre y vomita", "Consulta pediátrica de emergencia."),
    ("Sangrado abundante", "Acude a urgencias ahora."),
    ("El bebé presenta ictericia intensa", "Pediatra de inmediato."),
]


def crear_usuarios(session):
    insertados = 0
    for idx, uuid_str in enumerate(USUARIOS_FIJOS, 1):
        existe = session.execute(
            text("SELECT 1 FROM usuarios WHERE uuid = :u"), {"u": uuid_str}
        ).first()
        if not existe:
            session.execute(
                text("""
                    INSERT INTO usuarios (uuid, dispositivo_id, codigo_registro, email, password, nombre, baby_birthdate, fecha_consentimiento)
                    VALUES (:u, :d, :c, :e, :p, :n, :b, NOW())
                """),
                {
                    "u": uuid_str, 
                    "d": f"DISP-{uuid_str[-3:]}", 
                    "c": uuid_str[-6:].upper(),
                    "e": f"usuario{idx}@example.com",
                    "p": "hashed_password_123",  # En producción esto sería hasheado
                    "n": f"Usuario Prueba {idx}",
                    "b": "2023-01-01",
                },
            )
            insertados += 1
    session.commit()
    return insertados


def construir_interaccion(uuid_user: str, dia_offset: int, nivel: str):
    if nivel == "verde":
        riesgo = round(random.uniform(0.0, 0.3), 2)
        texto, respuesta = random.choice(PLANTILLAS_VERDE)
        sintomas_m = []
        sintomas_b = []
        accion = False
        reglas = ["regla_baseline"]
    elif nivel == "amarillo":
        riesgo = round(random.uniform(0.3, 0.7), 2)
        texto, respuesta = random.choice(PLANTILLAS_AMARILLO)
        sintomas_m = random.sample(SINTOMAS_MADRE[:4], k=random.randint(1, 2))
        sintomas_b = random.choice([[], [random.choice(SINTOMAS_BEBE[:3])]])
        accion = False
        reglas = ["regla_seguimiento"]
    else:  # rojo
        riesgo = round(random.uniform(0.7, 1.0), 2)
        texto, respuesta = random.choice(PLANTILLAS_ROJO)
        sintomas_m = random.sample(SINTOMAS_MADRE, k=random.randint(1, 3))
        sintomas_b = random.choice([[], random.sample(SINTOMAS_BEBE, k=random.randint(1, 2))])
        accion = True
        reglas = ["regla_emergencia"]

    fecha = datetime.utcnow() - timedelta(days=dia_offset, hours=random.randint(0, 23))

    return {
        "uuid": uuid_user,
        "fecha": fecha,
        "origen": random.choice(["voz", "texto"]),
        "texto_usuario": texto,
        "texto_respuesta": respuesta,
        "variables": "{}",
        "sintomas_madre": sintomas_m,
        "sintomas_bebe": sintomas_b,
        "nivel": nivel,
        "riesgo": riesgo,
        "recomendaciones": respuesta,
        "fuente": "guia_oms_2023",
        "reglas": reglas,
        "accion": accion,
    }


def insertar_interacciones(session):
    random.seed(42)  # determinista
    total = 0
    for uuid_user in USUARIOS_FIJOS:
        # 12 verdes, 6 amarillas, 2 rojas = 20
        niveles = (["verde"] * 12) + (["amarillo"] * 6) + (["rojo"] * 2)
        random.shuffle(niveles)
        # repartir en los últimos 30 días
        offsets = random.sample(range(1, 31), k=20)
        offsets.sort(reverse=True)

        for offset, nivel in zip(offsets, niveles):
            data = construir_interaccion(uuid_user, offset, nivel)
            session.execute(
                text("""
                    INSERT INTO interacciones
                        (usuario_uuid, fecha, origen, texto_usuario, texto_respuesta,
                         variables_extraidas, sintomas_madre, sintomas_bebe, nivel_alerta,
                         puntuacion_riesgo, recomendaciones, fuente, reglas_activadas,
                         requiere_accion_inmediata)
                    VALUES
                        (:uuid, :fecha, :origen, :texto_usuario, :texto_respuesta,
                         CAST(:variables AS JSONB), :sintomas_madre, :sintomas_bebe, :nivel,
                         :riesgo, :recomendaciones, :fuente, :reglas, :accion)
                """),
                data,
            )
            total += 1
    session.commit()
    return total


def main():
    session = Session()
    try:
        nuevos = crear_usuarios(session)
        print(f"→ {nuevos} usuario(s) nuevo(s) insertado(s) (3 esperados máximo)")
        total = insertar_interacciones(session)
        print(f"✅ Seed completado: {total} interacciones insertadas para {len(USUARIOS_FIJOS)} usuarios.")
    except Exception as e:
        session.rollback()
        print(f"❌ Error en seed: {e}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
