"""
Ejecuta las migraciones SQL (001 y 002) contra la base de datos.
Uso: python scripts/init_db.py
"""

import sys
from pathlib import Path

# Agregar raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from database import engine

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"

MIGRATION_FILES = [
    "001_create_tables.sql",
    "002_seed_test_users.sql",
]


def run_migrations():
    with engine.connect() as conn:
        for filename in MIGRATION_FILES:
            filepath = MIGRATIONS_DIR / filename
            print(f"Ejecutando {filename}...")
            sql = filepath.read_text(encoding="utf-8")
            conn.execute(text(sql))
            conn.commit()
            print(f"  ✔ {filename} completado")
    print("\nMigraciones ejecutadas correctamente.")


if __name__ == "__main__":
    run_migrations()
