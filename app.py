# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, or_
from datetime import datetime, date, timedelta
from functools import wraps
from flask_migrate import Migrate
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

import services.dashboard_service as dashboard_service

app = Flask(__name__)
app.secret_key = 'kitchenmetrics_2026_key'

# --- CONFIGURACIÓN DE BASE DE DATOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Nemo2002@localhost:5432/kitchenmetrics_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- MODELOS DE BASE DE DATOS ---

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

dashboard_service.init_objects(
    db,
    Reserva,
    JornadaCocina,
    MenuDia,
    MermaIngrediente,
    LoteIngrediente,
    Ingrediente,
    Usuario,
    Rol
)

# --- SEGURIDAD ---
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Sesión expirada.", "danger")
                return redirect(url_for('index'))
            if role and session.get('user_rol').lower() != role.lower():
                flash("Acceso denegado.", "danger")
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
        destinos = {'admin': 'admin_dashboard_principal', 'cocina': 'panel_cocina', 'funcionario': 'panel_funcionario'}
        return redirect(url_for(destinos.get(session['user_rol'], 'index')))
    flash("Credenciales incorrectas.", "danger")
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
    limite_hoy = datetime.combine(hoy, datetime.strptime("15:00", "%H:%M").time())

    reservas_vencidas = Reserva.query.join(JornadaCocina).join(MenuDia).filter(
        Reserva.id_usuario == user.id_usuario,
        Reserva.estado == 'confirmada',
        or_(MenuDia.fecha < hoy, (MenuDia.fecha == hoy) & (ahora > limite_hoy))
    ).all()

    if reservas_vencidas:
        for res in reservas_vencidas:
            res.estado = 'no_retirada'
            user.faltas_acumuladas += 1
        db.session.commit()

    manana = hoy + timedelta(days=1)
    jornadas = db.session.query(JornadaCocina).join(MenuDia).filter(
        MenuDia.estado == 'activo', MenuDia.fecha == manana
    ).all()
    reserva_activa = Reserva.query.filter_by(id_usuario=user.id_usuario, estado='confirmada').first()
    return render_template('funcionario.html', nombre=session['user_nombre'], jornadas=jornadas, faltas=user.faltas_acumuladas, reserva_activa=reserva_activa)

@app.route('/reservar/<int:id_jornada>', methods=['POST'])
@login_required(role='funcionario')
def reservar(id_jornada):
    jornada = db.session.get(JornadaCocina, id_jornada)
    if not jornada or jornada.raciones_disponibles <= 0:
        flash("Sin cupos disponibles para este menú.", "warning")
        return redirect(url_for('panel_funcionario'))

    try:
        nueva_reserva = Reserva(id_usuario=session['user_id'], id_jornada=id_jornada)
        jornada.raciones_disponibles -= 1
        db.session.add(nueva_reserva)
        db.session.commit()
        flash("¡Reserva exitosa!", "success")
    except Exception:
        db.session.rollback()
        flash("Ya reservaste y retiraste el menú de hoy", "danger")

    return redirect(url_for('panel_funcionario'))

@app.route('/retirar/<int:id_reserva>', methods=['POST'])
@login_required(role='funcionario')
def retirar(id_reserva):
    reserva = db.session.get(Reserva, id_reserva)
    user = Usuario.query.get(session['user_id'])
    pass_confirm = request.form.get('password_confirmacion')
    if reserva and user.contrasena == pass_confirm:
        reserva.estado = 'consumida'
        db.session.commit()
        flash("Retiro confirmado.", "success")
    else:
        flash("Clave incorrecta.", "danger")
    return redirect(url_for('panel_funcionario'))

@app.route('/admin')
@login_required(role='admin')
def panel_admin():
    return render_template('admin.html',
        nombre=session['user_nombre'],
        menus=MenuDia.query.all(),
        usuarios=Usuario.query.all())

@app.route('/admin/dashboard/principal')
@login_required(role='admin')
def admin_dashboard_principal():
    period = request.args.get('period', 'week')
    today, start_date, prev_start, prev_end, period_label = dashboard_service._period_bounds(period)
    current_reservas, previous_reservas = dashboard_service._reservas_base(start_date, today), dashboard_service._reservas_base(prev_start, prev_end)
    kpis = dashboard_service.calculate_dashboard_kpis(start_date, today, prev_start, prev_end, current_reservas, previous_reservas)
    listas, charts = dashboard_service.get_dashboard_lists(start_date, today, current_reservas), dashboard_service.generate_dashboard_charts(start_date, today)
    extras = {'usuarios_count': Usuario.query.count(),
              'menus_count': MenuDia.query.filter(MenuDia.fecha.between(start_date, today)).count()}
    return render_template('dashboard.html',
        nombre=session.get('user_nombre'), period=period, period_label=period_label,
        start_date_str=start_date.strftime('%Y-%m-%d'), today_str=today.strftime('%Y-%m-%d'),
        current_year=today.year, **kpis, **listas, **charts, **extras,
        **dashboard_service.get_inventory_context(),
        **dashboard_service.get_waste_context(start_date, today),
        **dashboard_service.get_users_context())

@app.route('/admin/usuario/crear', methods=['POST'])
@login_required(role='admin')
def admin_usuario_crear():
    try:
        id_rol = request.form.get('id_rol', type=int)
        rut, nombre, apellido = (request.form.get(f, '').strip() for f in ['rut','nombre','apellido'])
        email, contrasena = request.form.get('email','').strip().lower(), request.form.get('contrasena','').strip()
        faltas_acumuladas, estado = request.form.get('faltas_acumuladas', type=int) or 0, request.form.get('estado','activo').strip().lower()
        if not all([id_rol, rut, nombre, apellido, email, contrasena]): flash("Completa todos los campos obligatorios.","warning"); return redirect(request.referrer or url_for('admin_dashboard_principal'))
        if not db.session.get(Rol, id_rol): flash("El rol seleccionado no existe.","danger"); return redirect(request.referrer or url_for('admin_dashboard_principal'))
        db.session.add(Usuario(id_rol=id_rol, rut=rut, nombre=nombre, apellido=apellido, email=email, contrasena=contrasena, faltas_acumuladas=faltas_acumuladas, estado=estado))
        db.session.commit(); flash("Usuario creado correctamente.","success")
    except IntegrityError: db.session.rollback(); flash("No se pudo crear el usuario. Revisa RUT o email duplicado.","danger")
    except Exception: db.session.rollback(); flash("Ocurrió un error al crear el usuario.","danger")
    return redirect(request.referrer or url_for('admin_dashboard_principal'))

@app.route('/admin/usuario/editar/<int:id_usuario>', methods=['POST'])
@login_required(role='admin')
def admin_usuario_editar(id_usuario):
    usuario = db.session.get(Usuario, id_usuario)
    if not usuario: flash("Usuario no encontrado.","danger"); return redirect(request.referrer or url_for('admin_dashboard_principal'))
    try:
        id_rol = request.form.get('id_rol', type=int)
        rut, nombre, apellido = (request.form.get(f, '').strip() for f in ['rut','nombre','apellido'])
        email, contrasena = request.form.get('email','').strip().lower(), request.form.get('contrasena','').strip()
        faltas_acumuladas, estado = request.form.get('faltas_acumuladas', type=int), request.form.get('estado','').strip().lower()
        if not all([id_rol, rut, nombre, apellido, email]): flash("Completa los campos obligatorios.","warning"); return redirect(request.referrer or url_for('admin_dashboard_principal'))
        if not db.session.get(Rol, id_rol): flash("El rol seleccionado no existe.","danger"); return redirect(request.referrer or url_for('admin_dashboard_principal'))
        usuario.id_rol, usuario.rut, usuario.nombre, usuario.apellido, usuario.email = id_rol, rut, nombre, apellido, email
        if contrasena: usuario.contrasena = contrasena
        if faltas_acumuladas is not None: usuario.faltas_acumuladas = faltas_acumuladas
        if estado: usuario.estado = estado
        db.session.commit(); flash("Usuario actualizado correctamente.","success")
    except IntegrityError: db.session.rollback(); flash("No se pudo actualizar. RUT o email duplicado.","danger")
    except Exception: db.session.rollback(); flash("Ocurrió un error al actualizar el usuario.","danger")
    return redirect(request.referrer or url_for('admin_dashboard_principal'))

@app.route('/admin/usuario/eliminar/<int:id_usuario>', methods=['POST'])
@login_required(role='admin')
def admin_usuario_eliminar(id_usuario):
    usuario = db.session.get(Usuario, id_usuario)
    if not usuario: flash("Usuario no encontrado.","danger"); return redirect(request.referrer or url_for('admin_dashboard_principal'))
    try: db.session.delete(usuario); db.session.commit(); flash("Usuario eliminado correctamente.","success")
    except IntegrityError: db.session.rollback(); flash("No se puede eliminar este usuario porque tiene registros asociados.","danger")
    except Exception: db.session.rollback(); flash("Ocurrió un error al eliminar el usuario.","danger")
    return redirect(request.referrer or url_for('admin_dashboard_principal'))

@app.route('/admin/usuario/desbloquear/<int:id_usuario>', methods=['POST'])
@login_required(role='admin')
def admin_usuario_desbloquear(id_usuario):
    usuario = db.session.get(Usuario, id_usuario)
    if not usuario: flash("Usuario no encontrado.","danger"); return redirect(request.referrer or url_for('admin_dashboard_principal'))
    try: usuario.estado="activo"; db.session.commit(); flash("Usuario desbloqueado correctamente.","success")
    except Exception: db.session.rollback(); flash("Ocurrió un error al desbloquear el usuario.","danger")
    return redirect(request.referrer or url_for('admin_dashboard_principal'))


@app.route('/cocina')
@login_required(role='cocina')
def panel_cocina():
    modo = request.args.get('modo', 'hoy')

    if modo == 'manana':
        fecha_consulta = date.today() + timedelta(days=1)
        titulo_panel = "Planificación de Producción - MAÑANA"
    else:
        fecha_consulta = date.today()
        titulo_panel = "Panel de Control de Entregas - HOY"

    reservas_lista = Reserva.query.join(JornadaCocina).join(MenuDia).filter(
        MenuDia.fecha == fecha_consulta
    ).all()

    resumen_platos = {}
    calculo_ingredientes = {}
    indices_fondo = {0: 1, 1: 4, 2: 7}

    for r in reservas_lista:
        if r.estado != 'no_retirada':
            n_bandeja = r.id_jornada % 3
            idx = indices_fondo.get(n_bandeja, 1)

            if len(r.jornada.menu_dia.detalles) > idx:
                nombre_fondo = r.jornada.menu_dia.detalles[idx].plato.nombre
                resumen_platos[nombre_fondo] = resumen_platos.get(nombre_fondo, 0) + 1

                for detalle in r.jornada.menu_dia.detalles:
                    for item in detalle.plato.recetas:
                        ing = item.ingrediente
                        if ing.nombre not in calculo_ingredientes:
                            calculo_ingredientes[ing.nombre] = {'cantidad': 0, 'unidad': ing.unidad_medida}
                        calculo_ingredientes[ing.nombre]['cantidad'] += float(item.cantidad_por_porcion)

    return render_template(
        'cocina.html',
        nombre=session['user_nombre'],
        reservas=reservas_lista,
        resumen=resumen_platos,
        ingredientes=calculo_ingredientes,
        fecha_ver=fecha_consulta,
        titulo=titulo_panel,
        modo=modo,
        datetime=datetime
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)