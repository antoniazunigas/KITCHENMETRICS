from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'kitchenmetrics_2026_key'

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Nemo2002@localhost:5432/kitchenmetrics_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS ---
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(12), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), nullable=False) 
    faltas_acumuladas = db.Column(db.Integer, default=0)
    reservas = db.relationship('Reserva', backref='usuario', lazy=True)

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
    # Relación para sacar el nombre del plato fácil
    menu = db.relationship('Menu', backref='reservas_asociadas')

# --- SEGURIDAD ---
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Sesión expirada. Por favor inicie sesión.", "danger")
                return redirect(url_for('index'))
            if role and session.get('user_rol').lower() != role.lower():
                flash(f"Acceso denegado: Se requiere rol de {role}", "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- RUTAS ---
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    rut_raw = request.form.get('rut').strip().upper()
    rut_limpio = "".join(filter(lambda x: x.isdigit() or x == 'K', rut_raw))
    user = Usuario.query.filter_by(rut=rut_limpio).first()
    if user:
        session['user_id'] = user.id_usuario
        session['user_rol'] = user.rol
        session['user_nombre'] = user.nombre
        destinos = {'admin': 'panel_admin', 'cocina': 'panel_cocina', 'funcionario': 'panel_funcionario'}
        return redirect(url_for(destinos.get(user.rol.lower(), 'index')))
    flash("RUT no registrado.", "danger")
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/funcionario')
@login_required(role='funcionario')
def panel_funcionario():
    user = Usuario.query.get(session['user_id'])
    menus = Menu.query.all()
    # Buscamos si tiene una reserva activa que NO haya retirado aún
    reserva_activa = Reserva.query.filter_by(id_usuario=user.id_usuario, fue_retirado=False).first()
    
    return render_template('funcionario.html', 
                           nombre=session['user_nombre'], 
                           menus=menus, 
                           faltas=user.faltas_acumuladas,
                           reserva_activa=reserva_activa)

@app.route('/reservar/<int:id_menu>', methods=['POST'])
@login_required(role='funcionario')
def reservar(id_menu):
    # Verificar si ya tiene una reserva sin retirar
    existente = Reserva.query.filter_by(id_usuario=session['user_id'], fue_retirado=False).first()
    if existente:
        flash("Ya tienes una reserva activa. Debes retirarla antes de pedir otra.", "warning")
        return redirect(url_for('panel_funcionario'))

    nueva_reserva = Reserva(id_usuario=session['user_id'], id_menu=id_menu)
    db.session.add(nueva_reserva)
    db.session.commit()
    flash("Reserva realizada con éxito.", "success")
    return redirect(url_for('panel_funcionario'))

@app.route('/retirar/<int:id_reserva>', methods=['POST'])
@login_required(role='funcionario')
def retirar(id_reserva):
    reserva = Reserva.query.get(id_reserva)
    if reserva and reserva.id_usuario == session['user_id']:
        reserva.fue_retirado = True
        db.session.commit()
        flash("Almuerzo marcado como retirado. ¡Buen provecho!", "success")
    return redirect(url_for('panel_funcionario'))

@app.route('/admin')
@login_required(role='admin')
def panel_admin():
    menus = Menu.query.all()
    usuarios = Usuario.query.all()
    return render_template('admin.html', nombre=session['user_nombre'], menus=menus, usuarios=usuarios)

@app.route('/cocina')
@login_required(role='cocina')
def panel_cocina():
    reservas = Reserva.query.all()
    return render_template('cocina.html', nombre=session['user_nombre'], reservas=reservas)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)