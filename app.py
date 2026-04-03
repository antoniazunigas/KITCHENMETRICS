from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'kitchenmetrics_2026_key'

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Nemo2002@localhost:5432/kitchenmetrics_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS DE BASE DE DATOS ---

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(12), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), nullable=False) # admin, funcionario, cocina
    faltas_acumuladas = db.Column(db.Integer, default=0)

class Menu(db.Model):
    __tablename__ = 'menu'
    id_menu = db.Column(db.Integer, primary_key=True)
    nombre_plato = db.Column(db.String(100), nullable=False)
    tipo_dieta = db.Column(db.String(50)) 
    fecha_menu = db.Column(db.Date, nullable=False) 

class Reserva(db.Model):
    __tablename__ = 'reserva'
    id_reserva = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_menu = db.Column(db.Integer, db.ForeignKey('menu.id_menu'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    fue_retirado = db.Column(db.Boolean, default=False)
    es_saldo_liberado = db.Column(db.Boolean, default=False)

class Ingrediente(db.Model):
    __tablename__ = 'ingrediente'
    id_ingrediente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    unidad_medida = db.Column(db.String(20), nullable=False) 

class Receta(db.Model):
    __tablename__ = 'receta'
    id_receta = db.Column(db.Integer, primary_key=True)
    id_menu = db.Column(db.Integer, db.ForeignKey('menu.id_menu'), nullable=False)
    id_ingrediente = db.Column(db.Integer, db.ForeignKey('ingrediente.id_ingrediente'), nullable=False)
    cantidad_porcion = db.Column(db.Float, nullable=False) 

class AuditoriaMerma(db.Model):
    __tablename__ = 'auditoria_merma'
    id_auditoria = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    id_menu = db.Column(db.Integer, db.ForeignKey('menu.id_menu'), nullable=False)
    cantidad_producida_planificada = db.Column(db.Float) 
    cantidad_merma_fisica = db.Column(db.Float) 
    ieo_resultado = db.Column(db.Float) 

# --- SEGURIDAD ---
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Sesión expirada. Por favor inicie sesión.", "danger")
                return redirect(url_for('index'))
            if role and session.get('user_rol').lower() != role.lower():
                flash("Acceso denegado: No tiene permisos de " + role, "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- RUTAS DE ACCESO ---
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # Limpiamos el RUT de cualquier caracter que no sea número o K
    rut_raw = request.form.get('rut').strip().upper()
    rut_limpio = "".join(filter(lambda x: x.isdigit() or x == 'K', rut_raw))
    
    user = Usuario.query.filter_by(rut=rut_limpio).first()

    if user:
        session['user_id'] = user.id_usuario
        session['user_rol'] = user.rol
        session['user_nombre'] = user.nombre
        
        destinos = {'admin': 'panel_admin', 'cocina': 'panel_cocina', 'funcionario': 'panel_funcionario'}
        return redirect(url_for(destinos.get(user.rol.lower(), 'index')))
    
    flash("RUT no registrado en el sistema.", "danger")
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- PANELES PROTEGIDOS (Vistas iniciales) ---
@app.route('/admin')
@login_required(role='admin')
def panel_admin():
    return f"<h1>Panel Admin</h1><p>Bienvenido {session['user_nombre']}</p><a href='/logout'>Salir</a>"

@app.route('/funcionario')
@login_required(role='funcionario')
def panel_funcionario():
    return f"<h1>Panel Funcionario</h1><p>Hola {session['user_nombre']}</p><a href='/logout'>Salir</a>"

@app.route('/cocina')
@login_required(role='cocina')
def panel_cocina():
    return f"<h1>Panel Cocina</h1><p>Chef {session['user_nombre']}</p><a href='/logout'>Salir</a>"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)