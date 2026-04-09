from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, or_
from datetime import datetime, date, timedelta 
from functools import wraps
from flask_migrate import Migrate
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'kitchenmetrics_2026_key'

# --- CONFIGURACIÓN DE BASE DE DATOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Nemo2002@localhost:5432/kitchenmetrics_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- MODELOS DE BASE DE DATOS (Se mantienen igual) ---
class Rol(db.Model):
    __tablename__ = "rol"
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(15), nullable=False, unique=True)
    usuarios = db.relationship("Usuario", back_populates="rol")

class Usuario(db.Model):
    __tablename__ = "usuario"
    id_usuario = db.Column(db.Integer, primary_key=True)
    id_rol = db.Column(db.Integer, db.ForeignKey("rol.id_rol"), nullable=False)
    rut = db.Column(db.String(12), unique=True, nullable=False)
    nombre = db.Column(db.String(20), nullable=False)
    apellido = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False) 
    contrasena = db.Column(db.String(255), nullable=False)
    faltas_acumuladas = db.Column(db.Integer, nullable=False, default=0)
    estado = db.Column(db.String(10), nullable=False, default="activo")
    rol = db.relationship("Rol", back_populates="usuarios")
    reservas = db.relationship("Reserva", back_populates="usuario")

class MenuDia(db.Model):
    __tablename__ = "menu_dia"
    id_menu = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="activo")
    jornadas = db.relationship("JornadaCocina", back_populates="menu_dia")
    detalles = db.relationship("MenuDetalle", back_populates="menu_dia")

class Plato(db.Model):
    __tablename__ = "plato"
    id_plato = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False) 
    tipo_plato = db.Column(db.String(20), nullable=False)
    tipo_dieta = db.Column(db.String(30), nullable=True) 
    detalles = db.relationship("MenuDetalle", back_populates="plato")
    recetas = db.relationship("Receta", back_populates="plato")

class MenuDetalle(db.Model):
    __tablename__ = "menu_detalle"
    __table_args__ = (
        UniqueConstraint("id_menu", "id_plato", name="uq_menu_detalle_menu_plato"),
        UniqueConstraint("id_menu", "orden", name="uq_menu_detalle_menu_orden"),
    )
    id_menu_detalle = db.Column(db.Integer, primary_key=True)
    id_menu = db.Column(db.Integer, db.ForeignKey("menu_dia.id_menu"), nullable=False)
    id_plato = db.Column(db.Integer, db.ForeignKey("plato.id_plato"), nullable=False)
    orden = db.Column(db.Integer, nullable=False)
    menu_dia = db.relationship("MenuDia", back_populates="detalles")
    plato = db.relationship("Plato", back_populates="detalles")

class Ingrediente(db.Model):
    __tablename__ = "ingrediente"
    id_ingrediente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), nullable=False, unique=True)
    unidad_medida = db.Column(db.String(10), nullable=False)
    recetas = db.relationship("Receta", back_populates="ingrediente")
    lotes = db.relationship("LoteIngrediente", back_populates="ingrediente")

class LoteIngrediente(db.Model):
    __tablename__ = "lote_ingrediente"
    id_lote = db.Column(db.Integer, primary_key=True)
    id_ingrediente = db.Column(db.Integer, db.ForeignKey("ingrediente.id_ingrediente"), nullable=False)
    fecha_ingreso = db.Column(db.Date, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    cantidad_inicial = db.Column(db.Numeric(10, 3), nullable=False)
    cantidad_disponible = db.Column(db.Numeric(10, 3), nullable=False)
    costo_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    ingrediente = db.relationship("Ingrediente", back_populates="lotes")
    mermas = db.relationship("MermaIngrediente", back_populates="lote")

class Receta(db.Model):
    __tablename__ = "receta"
    __table_args__ = (UniqueConstraint("id_plato", "id_ingrediente", name="uq_receta_plato_ingrediente"),)
    id_receta = db.Column(db.Integer, primary_key=True)
    id_plato = db.Column(db.Integer, db.ForeignKey("plato.id_plato"), nullable=False)
    id_ingrediente = db.Column(db.Integer, db.ForeignKey("ingrediente.id_ingrediente"), nullable=False)
    cantidad_por_porcion = db.Column(db.Numeric(10, 3), nullable=False)
    plato = db.relationship("Plato", back_populates="recetas")
    ingrediente = db.relationship("Ingrediente", back_populates="recetas")

class JornadaCocina(db.Model):
    __tablename__ = "jornada_cocina"
    id_jornada = db.Column(db.Integer, primary_key=True)
    id_menu = db.Column(db.Integer, db.ForeignKey("menu_dia.id_menu"), nullable=False)
    raciones_planificadas = db.Column(db.Integer, nullable=False)
    raciones_preparadas = db.Column(db.Integer, nullable=False)
    raciones_disponibles = db.Column(db.Integer, nullable=False)
    menu_dia = db.relationship("MenuDia", back_populates="jornadas")
    reservas = db.relationship("Reserva", back_populates="jornada")
    consumos = db.relationship("Consumo", back_populates="jornada")
    mermas_preparadas = db.relationship("MermaPreparada", back_populates="jornada")

class Reserva(db.Model):
    __tablename__ = "reserva"
    __table_args__ = (UniqueConstraint("id_usuario", "id_jornada", name="uq_reserva_usuario_jornada"),)
    id_reserva = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_jornada = db.Column(db.Integer, db.ForeignKey("jornada_cocina.id_jornada"), nullable=False)
    fecha_reserva = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    estado = db.Column(db.String(20), nullable=False, default="confirmada")
    usuario = db.relationship("Usuario", back_populates="reservas")
    jornada = db.relationship("JornadaCocina", back_populates="reservas")
    consumo = db.relationship("Consumo", back_populates="reserva", uselist=False)

class Consumo(db.Model):
    __tablename__ = "consumo"
    id_consumo = db.Column(db.Integer, primary_key=True)
    id_reserva = db.Column(db.Integer, db.ForeignKey("reserva.id_reserva"), nullable=False, unique=True)
    id_jornada = db.Column(db.Integer, db.ForeignKey("jornada_cocina.id_jornada"), nullable=False)
    fecha_consumo = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    estado = db.Column(db.String(20), nullable=False, default="registrado")
    reserva = db.relationship("Reserva", back_populates="consumo")
    jornada = db.relationship("JornadaCocina", back_populates="consumos")

class MermaIngrediente(db.Model):
    __tablename__ = "merma_ingrediente"
    id_merma_ing = db.Column(db.Integer, primary_key=True)
    id_lote = db.Column(db.Integer, db.ForeignKey("lote_ingrediente.id_lote"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    cantidad = db.Column(db.Numeric(10, 3), nullable=False)
    costo_perdido = db.Column(db.Numeric(12, 2), nullable=False)
    motivo = db.Column(db.String(30), nullable=False)
    lote = db.relationship("LoteIngrediente", back_populates="mermas")

class MermaPreparada(db.Model):
    __tablename__ = "merma_preparada"
    id_merma_prep = db.Column(db.Integer, primary_key=True)
    id_jornada = db.Column(db.Integer, db.ForeignKey("jornada_cocina.id_jornada"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    cantidad_raciones = db.Column(db.Integer, nullable=False)
    costo_perdido = db.Column(db.Numeric(12, 2), nullable=False)
    motivo = db.Column(db.String(30), nullable=False)
    jornada = db.relationship("JornadaCocina", back_populates="mermas_preparadas")

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
    email_raw = request.form.get('email').strip().lower()
    pass_raw = request.form.get('password')
    user = Usuario.query.filter_by(email=email_raw).first()
    if user and user.contrasena == pass_raw:
        session['user_id'] = user.id_usuario
        session['user_rol'] = user.rol.nombre.lower()
        session['user_nombre'] = user.nombre
        destinos = {'admin': 'panel_admin', 'cocina': 'panel_cocina', 'funcionario': 'panel_funcionario'}
        return redirect(url_for(destinos.get(session['user_rol'], 'index')))
    flash("Correo o contraseña incorrectos.", "danger")
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/funcionario')
@login_required(role='funcionario')
def panel_funcionario():
    user = Usuario.query.get(session['user_id'])
    ahora = datetime.now()
    hoy = date.today()
    
    # --- LÓGICA AUTOMÁTICA DE FALTAS (15:00 HRS) ---
    # Creamos el objeto datetime para las 15:00 de hoy
    limite_hoy = datetime.combine(hoy, datetime.strptime("15:00", "%H:%M").time())
    
    # Buscamos reservas 'confirmadas' que ya pasaron de fecha O que son de hoy y ya son más de las 15:00
    reservas_vencidas = Reserva.query.join(JornadaCocina).join(MenuDia).filter(
        Reserva.id_usuario == user.id_usuario,
        Reserva.estado == 'confirmada',
        or_(
            MenuDia.fecha < hoy,
            (MenuDia.fecha == hoy) & (ahora > limite_hoy)
        )
    ).all()

    if reservas_vencidas:
        for res in reservas_vencidas:
            res.estado = 'no_retirada'
            user.faltas_acumuladas += 1
        db.session.commit()
        flash(f"Se registraron {len(reservas_vencidas)} falta(s) por no retirar tu almuerzo a tiempo.", "warning")

    # --- BUSCAR MENÚ DE MAÑANA ---
    manana = hoy + timedelta(days=1)
    jornadas = db.session.query(JornadaCocina).join(MenuDia).filter(
        MenuDia.estado == 'activo',
        MenuDia.fecha == manana
    ).all()
    
    reserva_activa = Reserva.query.filter_by(id_usuario=user.id_usuario, estado='confirmada').first()
    
    return render_template('funcionario.html', 
                           nombre=session['user_nombre'], 
                           jornadas=jornadas, 
                           faltas=user.faltas_acumuladas,
                           reserva_activa=reserva_activa)

@app.route('/reservar/<int:id_jornada>', methods=['POST'])
@login_required(role='funcionario')
def reservar(id_jornada):
    jornada = db.session.get(JornadaCocina, id_jornada)
    if not jornada or jornada.raciones_disponibles <= 0:
        flash("No hay raciones disponibles.", "warning")
        return redirect(url_for('panel_funcionario'))
    
    existente = Reserva.query.filter_by(id_usuario=session['user_id'], estado='confirmada').first()
    if existente:
        flash("Ya tienes una reserva activa.", "warning")
        return redirect(url_for('panel_funcionario'))
        
    nueva_reserva = Reserva(id_usuario=session['user_id'], id_jornada=id_jornada)
    jornada.raciones_disponibles -= 1
    db.session.add(nueva_reserva)
    db.session.commit()
    flash("Reserva realizada con éxito para mañana.", "success")
    return redirect(url_for('panel_funcionario'))

@app.route('/retirar/<int:id_reserva>', methods=['POST'])
@login_required(role='funcionario')
def retirar(id_reserva):
    reserva = db.session.get(Reserva, id_reserva)
    user = Usuario.query.get(session['user_id'])
    
    # Obtenemos la contraseña que el usuario escribió en el prompt del navegador
    pass_confirm = request.form.get('password_confirmacion')

    # VALIDACIÓN: La contraseña debe ser igual a la del usuario logueado
    if reserva and user.contrasena == pass_confirm:
        reserva.estado = 'consumida'
        db.session.commit()
        flash("Almuerzo retirado correctamente. ¡Buen provecho!", "success")
    else:
        flash("Contraseña incorrecta. No se pudo confirmar el retiro.", "danger")
        
    return redirect(url_for('panel_funcionario'))

@app.route('/admin')
@login_required(role='admin')
def panel_admin():
    menus = MenuDia.query.all()
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