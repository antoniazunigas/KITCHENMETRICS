# database_run.py

from pathlib import Path
from app import app, db

SQL_FILE = Path("database_seed.sql")

def run_sql_file(sql_path: Path) -> None:
    sql_text = sql_path.read_text(encoding="utf-8")
    # Usar conexión cruda para ejecutar scripts complejos / bloques DO $$
    with db.engine.raw_connection() as raw_conn:
        with raw_conn.cursor() as cur:
            cur.execute(sql_text)
        raw_conn.commit()

    print("BD poblada correctamente desde database_seed.sql")

if __name__ == "__main__":
    with app.app_context():
        # WARNING: esto eliminará todos los datos existentes en la base de datos, úsalo con precaución.
        db.drop_all()
        db.create_all()
        run_sql_file(SQL_FILE)