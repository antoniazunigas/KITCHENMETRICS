# database_run.py

from pathlib import Path
from app import app, db

SQL_FILE = Path("database_seed.sql")

def run_sql_file(sql_path: Path) -> None:
    if not sql_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {sql_path}")

    sql_text = sql_path.read_text(encoding="utf-8")

    # Separación simple por ';'
    # Importante: este seed no debe contener ';' dentro de strings.
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]

    with db.engine.begin() as connection:
        for stmt in statements:
            connection.exec_driver_sql(stmt)

    print("BD poblada correctamente desde database_seed.sql")

if __name__ == "__main__":
    with app.app_context():
        run_sql_file(SQL_FILE)