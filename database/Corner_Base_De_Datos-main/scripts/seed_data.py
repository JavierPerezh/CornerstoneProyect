"""
Inserta datos de ejemplo para los 3 usuarios de prueba.
Uso: python scripts/seed_data.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, text
from database import SessionLocal
from models import Usuario, Interaccion, Alerta, ProgresoDiario


def seed():
    db = SessionLocal()

    # Obtener usuarios de prueba
    usuarios = db.execute(
        select(Usuario).where(Usuario.uuid_anonimo.in_([
            "test-uuid-001", "test-uuid-002", "test-uuid-003"
        ]))
    ).scalars().all()

    if not usuarios:
        print("No se encontraron usuarios de prueba. Ejecuta primero: python scripts/init_db.py")
        return

    print(f"Encontrados {len(usuarios)} usuarios de prueba.\n")

    for user in usuarios:
        # Interacciones de ejemplo
        db.add(Interaccion(
            usuario_id=user.id,
            mensaje_usuario="Me siento muy cansada hoy",
            respuesta_bot="Es completamente normal sentir fatiga en esta etapa. ¿Cuántas horas dormiste anoche?",
        ))
        db.add(Interaccion(
            usuario_id=user.id,
            mensaje_usuario="Dormí solo 3 horas",
            respuesta_bot="Entiendo. Intenta descansar cuando el bebé duerma. Si la falta de sueño persiste, consulta con tu médico.",
        ))

        # Alertas de ejemplo
        db.add(Alerta(usuario_id=user.id, nivel="verde", motivo="Estado emocional estable"))
        db.add(Alerta(usuario_id=user.id, nivel="amarillo", motivo="Reporta fatiga constante por más de 3 días"))

        # Progreso diario
        db.add(ProgresoDiario(usuario_id=user.id, estado_animo=4, horas_sueno=6.5, notas="Buen día"))
        db.add(ProgresoDiario(usuario_id=user.id, estado_animo=2, horas_sueno=3.0, notas="Noche difícil"))
        db.add(ProgresoDiario(usuario_id=user.id, estado_animo=3, horas_sueno=5.0, notas="Regular"))

        print(f"  ✔ Datos insertados para {user.uuid_anonimo}")

    db.commit()
    db.close()
    print("\nSeed completado.")


if __name__ == "__main__":
    seed()
