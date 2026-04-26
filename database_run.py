import re
from pathlib import Path
from app import app, db, Usuario
from werkzeug.security import generate_password_hash

SQL_FILE = Path("database_seed.sql")

def run_sql_file(sql_path: Path) -> None:
    sql_text = sql_path.read_text(encoding="utf-8")
    
    # 1. Ejecutamos el SQL normalmente para crear la estructura y datos base
    with db.engine.raw_connection() as raw_conn:
        with raw_conn.cursor() as cur:
            cur.execute(sql_text)
        raw_conn.commit()

    # 2. Convertimos todas las contraseñas "1234" actuales en hashes
    # Esto asegura que todos los usuarios (incluyendo los 150 dummy) queden actualizados
    usuarios = Usuario.query.all()
    for u in usuarios:
        # Si la contraseña es corta (como '1234'), asumimos que no está hasheada y la hasheamos
        if len(u.contrasena) < 20: 
            u.set_password(u.contrasena)
    
    db.session.commit()
    print("BD poblada y contraseñas hasheadas correctamente.")

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        run_sql_file(SQL_FILE)