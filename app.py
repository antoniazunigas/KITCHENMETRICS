from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from datetime import datetime
from functools import wraps
from flask_migrate import Migrate


app = Flask(__name__)
app.secret_key = 'kitchenmetrics_2026_key'

# Configuración de base de datos
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Nemo2002@localhost:5432/kitchenmetrics_db' # Configuración para PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kitchenmetrics.db' # Configuración para SQLite (BD LOCAL)
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Migraciones: para manejar cambios en el modelo de datos


# --- MODELOS DE BASE DE DATOS ---

class Rol(db.Model):
    __tablename__ = "rol"
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(15), nullable=False, unique=True)
    usuarios = db.relationship("Usuario", back_populates="rol")
    def __repr__(self):
        return f"<Rol {self.nombre}>"

class Usuario(db.Model):
    __tablename__ = "usuario"
    id_usuario = db.Column(db.Integer, primary_key=True)
    id_rol = db.Column(db.Integer, db.ForeignKey("rol.id_rol"), nullable=False)
    rut = db.Column(db.String(12), unique=True, nullable=False)
    nombre = db.Column(db.String(20), nullable=False)
    apellido = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    faltas_acumuladas = db.Column(db.Integer, nullable=False, default=0)
    estado = db.Column(db.String(10), nullable=False, default="activo")  # activo / bloqueado
    rol = db.relationship("Rol", back_populates="usuarios")
    reservas = db.relationship("Reserva", back_populates="usuario")
    def __repr__(self):
        return f"<Usuario {self.nombre} {self.apellido}>"

class MenuDia(db.Model):
    __tablename__ = "menu_dia"
    id_menu = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="activo")  # activo / cerrado / borrador
    jornadas = db.relationship("JornadaCocina", back_populates="menu_dia")
    detalles = db.relationship("MenuDetalle", back_populates="menu_dia")
    def __repr__(self):
        return f"<MenuDia {self.fecha}>"
    
class Plato(db.Model):
    __tablename__ = "plato"
    id_plato = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), nullable=False)
    tipo_plato = db.Column(db.String(20), nullable=False)  # entrada, fondo, postre, etc.
    detalles = db.relationship("MenuDetalle", back_populates="plato")
    recetas = db.relationship("Receta", back_populates="plato")
    def __repr__(self):
        return f"<Plato {self.nombre}>"

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
    def __repr__(self):
        return f"<MenuDetalle menu={self.id_menu} plato={self.id_plato}>"

class Ingrediente(db.Model):
    __tablename__ = "ingrediente"
    id_ingrediente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), nullable=False, unique=True)
    unidad_medida = db.Column(db.String(10), nullable=False)
    recetas = db.relationship("Receta", back_populates="ingrediente")
    lotes = db.relationship("LoteIngrediente", back_populates="ingrediente")
    def __repr__(self):
        return f"<Ingrediente {self.nombre}>"


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
    def __repr__(self):
        return f"<LoteIngrediente {self.id_lote}>"


class Receta(db.Model):
    __tablename__ = "receta"
    __table_args__ = (
        UniqueConstraint("id_plato", "id_ingrediente", name="uq_receta_plato_ingrediente"),
    )
    id_receta = db.Column(db.Integer, primary_key=True)
    id_plato = db.Column(db.Integer, db.ForeignKey("plato.id_plato"), nullable=False)
    id_ingrediente = db.Column(db.Integer, db.ForeignKey("ingrediente.id_ingrediente"), nullable=False)
    cantidad_por_porcion = db.Column(db.Numeric(10, 3), nullable=False)
    plato = db.relationship("Plato", back_populates="recetas")
    ingrediente = db.relationship("Ingrediente", back_populates="recetas")
    def __repr__(self):
        return f"<Receta plato={self.id_plato} ingrediente={self.id_ingrediente}>"


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
    def __repr__(self):
        return f"<JornadaCocina {self.id_jornada}>"


class Reserva(db.Model):
    __tablename__ = "reserva"
    __table_args__ = (
        UniqueConstraint("id_usuario", "id_jornada", name="uq_reserva_usuario_jornada"),
    )
    id_reserva = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_jornada = db.Column(db.Integer, db.ForeignKey("jornada_cocina.id_jornada"), nullable=False)
    fecha_reserva = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    estado = db.Column(db.String(20), nullable=False, default="confirmada")
    # estados sugeridos: confirmada / cancelada / no_retirada / consumida
    usuario = db.relationship("Usuario", back_populates="reservas")
    jornada = db.relationship("JornadaCocina", back_populates="reservas")
    consumo = db.relationship("Consumo", back_populates="reserva", uselist=False)
    def __repr__(self):
        return f"<Reserva {self.id_reserva}>"


class Consumo(db.Model):
    __tablename__ = "consumo"
    __table_args__ = (
        UniqueConstraint("id_reserva", name="uq_consumo_reserva"),
    )
    id_consumo = db.Column(db.Integer, primary_key=True)
    id_reserva = db.Column(db.Integer, db.ForeignKey("reserva.id_reserva"), nullable=False, unique=True)
    id_jornada = db.Column(db.Integer, db.ForeignKey("jornada_cocina.id_jornada"), nullable=False)
    fecha_consumo = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    estado = db.Column(db.String(20), nullable=False, default="registrado")
    # estados sugeridos: registrado / anulado / parcial
    reserva = db.relationship("Reserva", back_populates="consumo")
    jornada = db.relationship("JornadaCocina", back_populates="consumos")
    def __repr__(self):
        return f"<Consumo {self.id_consumo}>"


class MermaIngrediente(db.Model):
    __tablename__ = "merma_ingrediente"
    id_merma_ing = db.Column(db.Integer, primary_key=True)
    id_lote = db.Column(db.Integer, db.ForeignKey("lote_ingrediente.id_lote"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    cantidad = db.Column(db.Numeric(10, 3), nullable=False)
    costo_perdido = db.Column(db.Numeric(12, 2), nullable=False)
    motivo = db.Column(db.String(30), nullable=False)
    lote = db.relationship("LoteIngrediente", back_populates="mermas")
    def __repr__(self):
        return f"<MermaIngrediente {self.id_merma_ing}>"


class MermaPreparada(db.Model):
    __tablename__ = "merma_preparada"
    id_merma_prep = db.Column(db.Integer, primary_key=True)
    id_jornada = db.Column(db.Integer, db.ForeignKey("jornada_cocina.id_jornada"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    cantidad_raciones = db.Column(db.Integer, nullable=False)
    costo_perdido = db.Column(db.Numeric(12, 2), nullable=False)
    motivo = db.Column(db.String(30), nullable=False)
    jornada = db.relationship("JornadaCocina", back_populates="mermas_preparadas")
    def __repr__(self):
        return f"<MermaPreparada {self.id_merma_prep}>"

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
        session['user_rol'] = user.rol.nombre  # Obtén el nombre del rol
        session['user_nombre'] = user.nombre
        destinos = {'admin': 'panel_admin', 'cocina': 'panel_cocina', 'funcionario': 'panel_funcionario'}
        return redirect(url_for(destinos.get(user.rol.nombre.lower(), 'index')))  # Usa .nombre aquí
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
    
    # Obtener jornadas activas (con sus menús asociados)
    jornadas = db.session.query(JornadaCocina).filter(
        JornadaCocina.raciones_disponibles > 0
    ).all()
    
    reserva_activa = Reserva.query.filter_by(id_usuario=user.id_usuario, estado='confirmada').first()
    
    return render_template('funcionario.html', 
                           nombre=session['user_nombre'], 
                           jornadas=jornadas,  # Cambia de 'menus' a 'jornadas'
                           faltas=user.faltas_acumuladas,
                           reserva_activa=reserva_activa)


@app.route('/reservar/<int:id_jornada>', methods=['POST'])
@login_required(role='funcionario')
def reservar(id_jornada):
    # Usar db.session.get() en lugar de .query.get()
    jornada = db.session.get(JornadaCocina, id_jornada)
    if not jornada:
        flash("Jornada no encontrada.", "danger")
        return redirect(url_for('panel_funcionario'))
    
    if jornada.raciones_disponibles <= 0:
        flash("No hay raciones disponibles para esta jornada.", "warning")
        return redirect(url_for('panel_funcionario'))
    
    existente = Reserva.query.filter_by(id_usuario=session['user_id'], estado='confirmada').first()
    if existente:
        flash("Ya tienes una reserva activa. Debes retirarla antes de pedir otra.", "warning")
        return redirect(url_for('panel_funcionario'))
    
    nueva_reserva = Reserva(id_usuario=session['user_id'], id_jornada=id_jornada, estado='confirmada')
    jornada.raciones_disponibles -= 1
    
    db.session.add(nueva_reserva)
    db.session.commit()
    flash("Reserva realizada con éxito.", "success")
    return redirect(url_for('panel_funcionario'))


@app.route('/retirar/<int:id_reserva>', methods=['POST'])
@login_required(role='funcionario')
def retirar(id_reserva):
    reserva = db.session.get(Reserva, id_reserva)
    if reserva and reserva.id_usuario == session['user_id']:
        reserva.estado = 'consumida'
        db.session.commit()
        flash("Almuerzo marcado como retirado. ¡Buen provecho!", "success")
    return redirect(url_for('panel_funcionario'))

@app.route('/admin')
@login_required(role='admin')
def panel_admin():
    menus = MenuDia.query.all()  # Cambiar Menu por MenuDia
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