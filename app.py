from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Nemo2002@localhost:5432/kitchenmetrics_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = 'usuario'
    Id_usuario = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Correo = db.Column(db.String(120), unique=True, nullable=False)
    Contraseña = db.Column(db.String(255), nullable=False)
    Rol = db.Column(db.String(50), nullable=False) # Admin, Funcionario, Visita

class Menu(db.Model):
    __tablename__ = 'menu'
    Id_menu = db.Column(db.Integer, primary_key=True)
    Nombre_plato = db.Column(db.String(100), nullable=False)
    Tipo_dieta = db.Column(db.String(50)) # Normal, Hipocalórico, Vegetariano
    Dia_semana = db.Column(db.String(20), nullable=False) 

class Reserva(db.Model):
    __tablename__ = 'reserva'
    Id_reserva = db.Column(db.Integer, primary_key=True)
    Id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.Id_usuario'), nullable=False)
    Id_menu = db.Column(db.Integer, db.ForeignKey('menu.Id_menu'), nullable=False)
    Fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    Fecha_consumo = db.Column(db.Date, nullable=False)

class Ingrediente(db.Model):
    __tablename__ = 'ingrediente'
    Id_ingrediente = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Unidad_medida = db.Column(db.String(20), nullable=False) # Gramos, CC, etc.

class Receta(db.Model):
    __tablename__ = 'receta'
    Id_receta = db.Column(db.Integer, primary_key=True)
    Id_menu = db.Column(db.Integer, db.ForeignKey('menu.Id_menu'), nullable=False)
    Id_ingrediente = db.Column(db.Integer, db.ForeignKey('ingrediente.Id_ingrediente'), nullable=False)
    Cantidad_porcion = db.Column(db.Float, nullable=False)

class Mermas(db.Model):
    __tablename__ = 'mermas'
    Id_mermas = db.Column(db.Integer, primary_key=True)
    Fecha = db.Column(db.Date, nullable=False)
    Cantidad_botada = db.Column(db.Float)
    Costo_perdido = db.Column(db.Integer)

with app.app_context():
    db.create_all()

@app.route('/')
def inicio():
    return "¡Tablas creadas y conexión exitosa!"

if __name__ == '__main__':
    app.run(debug=True)