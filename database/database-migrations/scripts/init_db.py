"""
Inicializa la base de datos ejecutando las migraciones SQL en orden.
Uso: python database-migrations/scripts/init_db.py
"""

import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = ROOT / "backend_api" / ".env"
MIGRATIONS_DIR = ROOT / "database" / "database-migrations" / "migrations"

MIGRATION_FILES = [
    "001_create_tables.sql",
    "002_add_indexes.sql",
    "003_add_views.sql",
]


def main():
    load_dotenv(ENV_PATH)
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print(f"❌ DATABASE_URL no encontrada en {ENV_PATH}")
        sys.exit(1)

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            for filename in MIGRATION_FILES:
                filepath = MIGRATIONS_DIR / filename
                print(f"→ Ejecutando {filename}...")
                cur.execute(filepath.read_text(encoding="utf-8"))
        conn.commit()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al inicializar: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
