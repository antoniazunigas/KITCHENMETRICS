# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, or_
from datetime import datetime, date, timedelta
from functools import wraps
from flask_migrate import Migrate
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from flask import Response, request
import csv
import io
from werkzeug.security import generate_password_hash, check_password_hash


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
# hashing
    def set_password(self, password):
        self.contrasena = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.contrasena, password)

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
    if user and user.check_password(pass_raw):
        session['user_id'] = user.id_usuario
        session['user_rol'] = user.rol.nombre.lower()
        session['user_nombre'] = user.nombre
        destinos = {'admin': 'admin_dashboard_principal', 'jefe_cocina': 'panel_jefe_cocina', 'funcionario': 'panel_funcionario'}
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
        rut, nombre, apellido = (request.form.get(f, '').strip() for f in ['rut', 'nombre', 'apellido'])
        email = request.form.get('email', '').strip().lower()
        contrasena = request.form.get('contrasena', '').strip()
        faltas_acumuladas = request.form.get('faltas_acumuladas', type=int) or 0
        estado = request.form.get('estado', 'activo').strip().lower()

        if not all([id_rol, rut, nombre, apellido, email, contrasena]):
            flash("Completa todos los campos obligatorios.", "warning")
            return redirect(request.referrer or url_for('admin_dashboard_principal'))

        if not db.session.get(Rol, id_rol):
            flash("El rol seleccionado no existe.", "danger")
            return redirect(request.referrer or url_for('admin_dashboard_principal'))

        # Creamos la instancia sin la contraseña inicialmente
        nuevo_usuario = Usuario(
            id_rol=id_rol, 
            rut=rut, 
            nombre=nombre, 
            apellido=apellido, 
            email=email, 
            faltas_acumuladas=faltas_acumuladas, 
            estado=estado
        )
        
        # Hasheamos la contraseña usando el método del modelo
        nuevo_usuario.set_password(contrasena)
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Usuario creado correctamente.", "success")

    except IntegrityError:
        db.session.rollback()
        flash("No se pudo crear el usuario. Revisa RUT o email duplicado.", "danger")
    except Exception:
        db.session.rollback()
        flash("Ocurrió un error al crear el usuario.", "danger")
        
    return redirect(request.referrer or url_for('admin_dashboard_principal'))

@app.route('/admin/usuario/editar/<int:id_usuario>', methods=['POST'])
@login_required(role='admin')
def admin_usuario_editar(id_usuario):
    usuario = db.session.get(Usuario, id_usuario)
    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(request.referrer or url_for('admin_dashboard_principal'))

    try:
        id_rol = request.form.get('id_rol', type=int)
        rut, nombre, apellido = (request.form.get(f, '').strip() for f in ['rut', 'nombre', 'apellido'])
        email = request.form.get('email', '').strip().lower()
        contrasena = request.form.get('contrasena', '').strip()
        faltas_acumuladas = request.form.get('faltas_acumuladas', type=int)
        estado = request.form.get('estado', '').strip().lower()

        if not all([id_rol, rut, nombre, apellido, email]):
            flash("Completa los campos obligatorios.", "warning")
            return redirect(request.referrer or url_for('admin_dashboard_principal'))

        if not db.session.get(Rol, id_rol):
            flash("El rol seleccionado no existe.", "danger")
            return redirect(request.referrer or url_for('admin_dashboard_principal'))

        # Actualizamos datos básicos
        usuario.id_rol = id_rol
        usuario.rut = rut
        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.email = email
        
        # Hashear solo si se ingresó una nueva contraseña en el formulario
        if contrasena:
            usuario.set_password(contrasena)
            
        if faltas_acumuladas is not None:
            usuario.faltas_acumuladas = faltas_acumuladas
        if estado:
            usuario.estado = estado

        db.session.commit()
        flash("Usuario actualizado correctamente.", "success")

    except IntegrityError:
        db.session.rollback()
        flash("No se pudo actualizar. RUT o email duplicado.", "danger")
    except Exception:
        db.session.rollback()
        flash("Ocurrió un error al actualizar el usuario.", "danger")
        
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


# REPORTEES CSV PARA DESCARGA DESDE DASHBOARD
@app.route('/admin/dashboard/exportar-csv')
@login_required(role='admin')
def admin_dashboard_exportar_csv():
    period = request.args.get('period', 'week')
    today, start_date, prev_start, prev_end, period_label = dashboard_service._period_bounds(period)

    rows = db.session.execute(
        db.text("""
            SELECT
                fecha,
                tipo_reporte,
                total_reservas,
                total_consumidas,
                total_no_retiradas,
                total_canceladas,
                tasa_faltas,
                total_ingredientes_lote,
                total_stock_disponible,
                total_merma_ingrediente,
                total_merma_preparada,
                costo_total_perdido,
                actualizado_en
            FROM reporte_operativo
            WHERE fecha BETWEEN :start_date AND :today
            ORDER BY fecha ASC, tipo_reporte ASC
        """),
        {"start_date": start_date, "today": today}
    ).mappings().all()

    output = io.StringIO()
    output.write('\ufeff')  # ayuda a Excel con acentos

    writer = csv.writer(output, delimiter=';')
    writer.writerow([
        'fecha',
        'tipo_reporte',
        'total_reservas',
        'total_consumidas',
        'total_no_retiradas',
        'total_canceladas',
        'tasa_faltas',
        'total_ingredientes_lote',
        'total_stock_disponible',
        'total_merma_ingrediente',
        'total_merma_preparada',
        'costo_total_perdido',
        'actualizado_en'
    ])

    for row in rows:
        writer.writerow([
            row['fecha'],
            row['tipo_reporte'],
            row['total_reservas'],
            row['total_consumidas'],
            row['total_no_retiradas'],
            row['total_canceladas'],
            row['tasa_faltas'],
            row['total_ingredientes_lote'],
            row['total_stock_disponible'],
            row['total_merma_ingrediente'],
            row['total_merma_preparada'],
            row['costo_total_perdido'],
            row['actualizado_en']
        ])

    csv_data = output.getvalue()
    output.close()

    filename = f"reporte_operativo_{period}_{today.isoformat()}.csv"

    return Response(
        csv_data,
        mimetype='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': f'attachment; filename={filename}'
        }
    )



@app.route('/cocina')
@login_required(role='cocina')
def panel_cocina():
    modo = request.args.get('modo', 'hoy')
    fecha_consulta = date.today() + timedelta(days=1) if modo == 'manana' else date.today()
    titulo_panel = "Planificación de Producción - MAÑANA" if modo == 'manana' else "Panel de Control de Entregas - HOY"

    reservas_lista = Reserva.query.join(JornadaCocina).join(MenuDia).filter(MenuDia.fecha == fecha_consulta).all()

    resumen_platos = {}
    calculo_ingredientes = {}

    for r in reservas_lista:
        if r.estado != 'no_retirada':
            # 1. Identificar la opción de fondo (1, 2 o 3)
            n_opcion = (r.id_jornada % 3)
            orden_fondo = 2 if n_opcion == 1 else (3 if n_opcion == 2 else 4)

            # 2. Recorrer platos del menú de ese día
            for detalle in r.jornada.menu_dia.detalles:
                nom = detalle.plato.nombre
                
                # Sumamos el fondo elegido, la entrada (orden 1) y el postre (orden 5)
                if detalle.orden == orden_fondo or detalle.orden == 1 or detalle.orden == 5:
                    resumen_platos[nom] = resumen_platos.get(nom, 0) + 1

                # 3. CÁLCULO DE INSUMOS
                if detalle.plato.recetas:
                    for item in detalle.plato.recetas:
                        ing_nombre = str(item.ingrediente.nombre)
                        if ing_nombre not in calculo_ingredientes:
                            calculo_ingredientes[ing_nombre] = {
                                'cantidad': 0.0, 
                                'unidad': str(item.ingrediente.unidad_medida)
                            }
                        
                        try:
                            valor_nuevo = float(item.cantidad_por_porcion)
                            valor_actual = float(calculo_ingredientes[ing_nombre]['cantidad'])
                            calculo_ingredientes[ing_nombre]['cantidad'] = valor_actual + valor_nuevo
                        except (ValueError, TypeError):
                            continue

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


@app.route('/jefe_cocina/dashboard')
@login_required(role='jefe_cocina')
def panel_jefe_cocina():
    period = request.args.get('period', 'week')
    today, start_date, prev_start, prev_end, period_label = dashboard_service._period_bounds(period)
    current_reservas = dashboard_service._reservas_base(start_date, today)
    previous_reservas = dashboard_service._reservas_base(prev_start, prev_end)
    kpis = dashboard_service.calculate_dashboard_kpis(start_date, today, prev_start, prev_end, current_reservas, previous_reservas)
    listas = dashboard_service.get_dashboard_lists(start_date, today, current_reservas)
    charts = dashboard_service.generate_dashboard_charts(start_date, today)
    waste = dashboard_service.get_waste_context(start_date, today)

    # Para planificación: dict fecha_iso -> {id_menu, estado, detalles, jornada}
    menus = MenuDia.query.filter(MenuDia.fecha >= today).order_by(MenuDia.fecha).all()
    menus_por_fecha = {str(m.fecha): {'id_menu': m.id_menu, 'estado': m.estado,
        'detalles': [{'orden': d.orden, 'id_plato': d.id_plato} for d in m.detalles],
        'jornada': {'raciones_planificadas': m.jornadas[0].raciones_planificadas if m.jornadas else 100}} for m in menus}
    platos_list = [{'id_plato': p.id_plato, 'nombre': p.nombre, 'tipo_plato': p.tipo_plato, 'tipo_dieta': p.tipo_dieta} for p in Plato.query.all()]

    # Para mermas: dict fecha_iso -> {count}
    from sqlalchemy import func
    rows = db.session.query(MermaIngrediente.fecha, func.count()).group_by(MermaIngrediente.fecha).filter(MermaIngrediente.fecha >= start_date).all()
    mermas_por_fecha = {str(r[0]): {'count': r[1]} for r in rows}

    return render_template('jefe_cocina.html',
        nombre=session.get('user_nombre'), period=period, period_label=period_label,
        start_date_str=start_date.strftime('%Y-%m-%d'), today_str=today.strftime('%Y-%m-%d'),
        current_year=today.year, menus_por_fecha=menus_por_fecha, platos_list=platos_list,
        mermas_por_fecha=mermas_por_fecha, lotes_list=LoteIngrediente.query.all(),
        jornadas_list=JornadaCocina.query.order_by(JornadaCocina.id_jornada.desc()).limit(30).all(),
        **kpis, **listas, **charts, **waste)


# ============================================================
# ENDPOINTS JSON — Panel Jefe de Cocina
# ============================================================

# ----------------------------------------------------------
# 1. GUARDAR / CREAR menú del día (planificación)
# ----------------------------------------------------------
@app.route('/jc/menu/guardar', methods=['POST'])
@login_required(role='jefe_cocina')
def jc_menu_guardar():
    """
    Recibe: { fecha, id_menu (null si nuevo), estado,
              detalles: [{orden, id_plato}],
              raciones_planificadas, raciones_preparadas, raciones_disponibles }
    Devuelve: { success, menu: {id_menu, estado, detalles, jornada} }
    """
    from flask import jsonify
    data = request.get_json(silent=True) or {}

    fecha_str          = data.get('fecha')
    id_menu            = data.get('id_menu')
    estado             = data.get('estado', 'activo')
    detalles_payload   = data.get('detalles', [])
    raciones_plan      = int(data.get('raciones_planificadas', 100))
    raciones_prep      = int(data.get('raciones_preparadas', 0))
    raciones_disp      = int(data.get('raciones_disponibles', 0))

    if not fecha_str:
        return jsonify({'success': False, 'error': 'Fecha requerida'}), 400

    try:
        fecha_obj = date.fromisoformat(fecha_str)
    except ValueError:
        return jsonify({'success': False, 'error': 'Fecha inválida'}), 400

    try:
        # ── Obtener o crear MenuDia ──
        if id_menu:
            menu = db.session.get(MenuDia, int(id_menu))
            if not menu:
                return jsonify({'success': False, 'error': 'Menú no encontrado'}), 404
            menu.estado = estado
        else:
            # Verificar si ya existe un menú para esa fecha
            menu = MenuDia.query.filter_by(fecha=fecha_obj).first()
            if menu:
                menu.estado = estado
            else:
                menu = MenuDia(fecha=fecha_obj, estado=estado)
                db.session.add(menu)
                db.session.flush()   # necesitamos el id_menu antes de los detalles

        # ── Actualizar detalles (borrar y reinsertar) ──
        MenuDetalle.query.filter_by(id_menu=menu.id_menu).delete()
        for det in detalles_payload:
            nuevo_det = MenuDetalle(
                id_menu=menu.id_menu,
                id_plato=int(det['id_plato']),
                orden=int(det['orden'])
            )
            db.session.add(nuevo_det)

        # ── Obtener o crear JornadaCocina ──
        jornada = JornadaCocina.query.filter_by(id_menu=menu.id_menu).first()
        if jornada:
            jornada.raciones_planificadas = raciones_plan
            jornada.raciones_preparadas   = raciones_prep
            jornada.raciones_disponibles  = raciones_disp
        else:
            jornada = JornadaCocina(
                id_menu=menu.id_menu,
                raciones_planificadas=raciones_plan,
                raciones_preparadas=raciones_prep,
                raciones_disponibles=raciones_disp
            )
            db.session.add(jornada)

        db.session.commit()

        # ── Construir respuesta para actualizar el calendário en JS ──
        detalles_resp = [{'orden': d.orden, 'id_plato': d.id_plato} for d in
                         MenuDetalle.query.filter_by(id_menu=menu.id_menu).all()]
        menu_resp = {
            'id_menu': menu.id_menu,
            'estado': menu.estado,
            'detalles': detalles_resp,
            'jornada': {
                'raciones_planificadas': jornada.raciones_planificadas,
                'raciones_preparadas':   jornada.raciones_preparadas,
                'raciones_disponibles':  jornada.raciones_disponibles,
            }
        }
        return jsonify({'success': True, 'menu': menu_resp})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ----------------------------------------------------------
# 2. ELIMINAR menú del día
# ----------------------------------------------------------
@app.route('/jc/menu/eliminar', methods=['POST'])
@login_required(role='jefe_cocina')
def jc_menu_eliminar():
    from flask import jsonify
    data = request.get_json(silent=True) or {}
    id_menu = data.get('id_menu')

    if not id_menu:
        return jsonify({'success': False, 'error': 'id_menu requerido'}), 400

    menu = db.session.get(MenuDia, int(id_menu))
    if not menu:
        return jsonify({'success': False, 'error': 'Menú no encontrado'}), 404

    try:
        # 🔴 VALIDACIÓN CLAVE
        jornadas_con_reservas = [
            j for j in menu.jornadas if j.reservas
        ]

        if jornadas_con_reservas:
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar el menú porque tiene reservas asociadas.'
            }), 400

        # 🧹 borrar detalles
        MenuDetalle.query.filter_by(id_menu=menu.id_menu).delete()

        # 🧹 borrar jornadas (todas, ya que no tienen reservas)
        for j in menu.jornadas:
            db.session.delete(j)

        # 🧹 borrar menú
        db.session.delete(menu)

        db.session.commit()
        return jsonify({'success': True})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ----------------------------------------------------------
# 3. REGISTRAR merma de ingrediente (por lote)
# ----------------------------------------------------------
@app.route('/jc/merma/ingrediente/registrar', methods=['POST'])
@login_required(role='jefe_cocina')
def jc_merma_ingrediente_registrar():
    """
    Recibe: { fecha, id_lote, cantidad, costo_perdido, motivo }
    Devuelve: { success }
    Además descuenta la cantidad del stock del lote.
    """
    from flask import jsonify
    data = request.get_json(silent=True) or {}

    fecha_str     = data.get('fecha')
    id_lote       = data.get('id_lote')
    cantidad      = data.get('cantidad')
    costo_perdido = data.get('costo_perdido', 0)
    motivo        = data.get('motivo', 'otro')

    if not all([fecha_str, id_lote, cantidad]):
        return jsonify({'success': False, 'error': 'Faltan campos obligatorios'}), 400

    try:
        fecha_obj = date.fromisoformat(fecha_str)
    except ValueError:
        return jsonify({'success': False, 'error': 'Fecha inválida'}), 400

    lote = db.session.get(LoteIngrediente, int(id_lote))
    if not lote:
        return jsonify({'success': False, 'error': 'Lote no encontrado'}), 404

    cantidad_float = float(cantidad)
    if cantidad_float <= 0:
        return jsonify({'success': False, 'error': 'La cantidad debe ser mayor que cero'}), 400

    if float(lote.cantidad_disponible) < cantidad_float:
        return jsonify({'success': False,
                        'error': f'Stock insuficiente. Disponible: {lote.cantidad_disponible}'}), 400

    try:
        # Registrar merma
        nueva_merma = MermaIngrediente(
            id_lote=lote.id_lote,
            fecha=fecha_obj,
            cantidad=cantidad_float,
            costo_perdido=float(costo_perdido),
            motivo=motivo
        )
        db.session.add(nueva_merma)

        # Descontar del stock del lote
        lote.cantidad_disponible = float(lote.cantidad_disponible) - cantidad_float

        db.session.commit()
        return jsonify({'success': True})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ----------------------------------------------------------
# 4. REGISTRAR merma de platos preparados no consumidos
# ----------------------------------------------------------
@app.route('/jc/merma/plato/registrar', methods=['POST'])
@login_required(role='jefe_cocina')
def jc_merma_plato_registrar():
    """
    Recibe: { fecha, id_jornada (opcional), cantidad_raciones, costo_perdido, motivo }
    Devuelve: { success }
    """
    from flask import jsonify
    data = request.get_json(silent=True) or {}

    fecha_str         = data.get('fecha')
    id_jornada        = data.get('id_jornada')
    cantidad_raciones = data.get('cantidad_raciones')
    costo_perdido     = data.get('costo_perdido', 0)
    motivo            = data.get('motivo', 'sobrante')

    if not all([fecha_str, cantidad_raciones]):
        return jsonify({'success': False, 'error': 'Faltan campos obligatorios'}), 400

    try:
        fecha_obj = date.fromisoformat(fecha_str)
    except ValueError:
        return jsonify({'success': False, 'error': 'Fecha inválida'}), 400

    cantidad_int = int(cantidad_raciones)
    if cantidad_int <= 0:
        return jsonify({'success': False, 'error': 'La cantidad debe ser mayor que cero'}), 400

    # Si no se pasó id_jornada, intentar inferirlo por fecha
    if not id_jornada:
        menu = MenuDia.query.filter_by(fecha=fecha_obj).first()
        if menu and menu.jornadas:
            id_jornada = menu.jornadas[0].id_jornada

    if not id_jornada:
        return jsonify({'success': False,
                        'error': 'No se encontró jornada para esa fecha. Selecciónala manualmente.'}), 400

    jornada = db.session.get(JornadaCocina, int(id_jornada))
    if not jornada:
        return jsonify({'success': False, 'error': 'Jornada no encontrada'}), 404

    try:
        nueva_merma = MermaPreparada(
            id_jornada=jornada.id_jornada,
            fecha=fecha_obj,
            cantidad_raciones=cantidad_int,
            costo_perdido=float(costo_perdido),
            motivo=motivo
        )
        db.session.add(nueva_merma)
        db.session.commit()
        return jsonify({'success': True})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)