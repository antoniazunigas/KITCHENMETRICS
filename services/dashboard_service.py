# dashboard_service.py
from datetime import date, timedelta
from sqlalchemy import func
from sqlalchemy.orm import selectinload

_db = None
Reserva = None
JornadaCocina = None
MenuDia = None
MermaIngrediente = None
LoteIngrediente = None
Ingrediente = None
Usuario = None
Rol = None


def init_objects(db, reserva, jornada_cocina, menu_dia, merma_ingrediente, lote_ingrediente, ingrediente, usuario, rol):
    global _db, Reserva, JornadaCocina, MenuDia, MermaIngrediente, LoteIngrediente, Ingrediente, Usuario, Rol
    _db = db
    Reserva = reserva
    JornadaCocina = jornada_cocina
    MenuDia = menu_dia
    MermaIngrediente = merma_ingrediente
    LoteIngrediente = lote_ingrediente
    Ingrediente = ingrediente
    Usuario = usuario
    Rol = rol


def _app_objects():
    if _db is None:
        raise RuntimeError("dashboard_service.init_objects() no fue ejecutado todavía.")
    return _db, Reserva, JornadaCocina, MenuDia, MermaIngrediente, LoteIngrediente, Ingrediente, Usuario, Rol


def _period_bounds(period: str):
    today = date.today()
    mapping = {'week': 7, 'month': 30, '6months': 180, 'year': 365}
    days = mapping.get(period, 7)

    start_date = today - timedelta(days=days)
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)

    labels = {
        'week': 'Última semana',
        'month': 'Último mes',
        '6months': 'Últimos 6 meses',
        'year': 'Último año'
    }

    return today, start_date, prev_start, prev_end, labels.get(period, 'Última semana')


def _reservas_base(start_date, end_date):
    db, Reserva, JornadaCocina, MenuDia, *_ = _app_objects()
    return (
        Reserva.query.join(JornadaCocina).join(MenuDia)
        .filter(MenuDia.fecha >= start_date, MenuDia.fecha <= end_date)
    )


def _dict_from_rows(rows, cast=float, default=0.0):
    return {k: (cast(v) if v is not None else default) for k, v in rows}


def _int_dict_from_rows(rows, default=0):
    return {k: (int(v) if v is not None else default) for k, v in rows}


def _date_series(start_date, end_date):
    return [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]


def calculate_dashboard_kpis(start_date, today, prev_start, prev_end, current_reservas, previous_reservas):
    db, Reserva, JornadaCocina, MenuDia, MermaIngrediente, LoteIngrediente, Ingrediente, Usuario, Rol = _app_objects()

    total_reservas = current_reservas.count()
    consumidas = current_reservas.filter(Reserva.estado == 'consumida').count()

    def _get_merma(inicio, fin):
        qty = db.session.query(func.coalesce(func.sum(MermaIngrediente.cantidad), 0)).filter(
            MermaIngrediente.fecha >= inicio, MermaIngrediente.fecha <= fin
        ).scalar() or 0

        cost = db.session.query(func.coalesce(func.sum(MermaIngrediente.costo_perdido), 0)).filter(
            MermaIngrediente.fecha >= inicio, MermaIngrediente.fecha <= fin
        ).scalar() or 0

        return qty, cost

    total_merma_qty, total_merma_cost = _get_merma(start_date, today)
    prev_total_merma_qty, _ = _get_merma(prev_start, prev_end)
    prev_total_reservas = previous_reservas.count()

    percent_desperdicio = round(
        (float(total_merma_qty) / (float(total_reservas) if total_reservas > 0 else 1)) * 100, 1
    )
    prev_percent_desperdicio = round(
        (float(prev_total_merma_qty) / (float(prev_total_reservas) if prev_total_reservas > 0 else 1)) * 100, 1
    )

    antes, actual, meta = round(prev_percent_desperdicio, 1), round(percent_desperdicio, 1), 15.0
    ya_reducido = round(max(antes - actual, 0), 1)

    if antes > meta:
        progress_percent = round(max(min(((antes - actual) / (antes - meta)) * 100, 100), 0), 1)
    else:
        progress_percent = 100.0 if actual <= meta else 0.0

    return {
        'total_reservas': total_reservas,
        'confirmadas': current_reservas.filter(Reserva.estado == 'confirmada').count(),
        'consumidas': consumidas,
        'no_retiradas': current_reservas.filter(Reserva.estado.in_(['no_retirada', 'no_consumida', 'cancelada'])).count(),
        'tasa_consumo': round((consumidas / total_reservas * 100), 1) if total_reservas > 0 else 0.0,
        'total_merma_qty': total_merma_qty,
        'total_merma_cost': total_merma_cost,
        'percent_desperdicio': percent_desperdicio,
        'antes': antes,
        'actual': actual,
        'meta': meta,
        'ya_reducido': ya_reducido,
        'progress_percent': progress_percent
    }


def get_dashboard_lists(start_date, today, current_reservas):
    db, Reserva, JornadaCocina, MenuDia, MermaIngrediente, LoteIngrediente, Ingrediente, Usuario, Rol = _app_objects()

    jornadas = JornadaCocina.query.join(MenuDia).filter(
        MenuDia.fecha >= start_date, MenuDia.fecha <= today
    ).order_by(JornadaCocina.id_jornada.desc()).limit(6).all()

    reservas_recientes = current_reservas.order_by(Reserva.fecha_reserva.desc()).limit(10).all()

    mermas = MermaIngrediente.query.filter(
        MermaIngrediente.fecha >= start_date, MermaIngrediente.fecha <= today
    ).order_by(MermaIngrediente.fecha.desc()).limit(10).all()

    lots_q = (
        LoteIngrediente.query
        .filter(LoteIngrediente.fecha_vencimiento != None)
        .order_by(LoteIngrediente.fecha_vencimiento.asc())
        .limit(6)
        .all()
    )

    lots_near = [{
        'nombre': lote.ingrediente.nombre,
        'cantidad': float(lote.cantidad_disponible),
        'unidad': lote.ingrediente.unidad_medida,
        'days_left': (lote.fecha_vencimiento - today).days if lote.fecha_vencimiento else None
    } for lote in lots_q]

    return {
        'jornadas': jornadas,
        'reservas_recientes': reservas_recientes,
        'mermas': mermas,
        'lots_near': lots_near
    }


def generate_dashboard_charts(start_date, today):
    db, Reserva, JornadaCocina, MenuDia, MermaIngrediente, LoteIngrediente, Ingrediente, Usuario, Rol = _app_objects()

    dates = _date_series(start_date, today)
    labels = [d.strftime('%d-%m') for d in dates]

    rows_total = db.session.query(MenuDia.fecha, func.count(Reserva.id_reserva)) \
        .join(JornadaCocina, Reserva.id_jornada == JornadaCocina.id_jornada) \
        .join(MenuDia, JornadaCocina.id_menu == MenuDia.id_menu) \
        .filter(MenuDia.fecha >= start_date, MenuDia.fecha <= today) \
        .group_by(MenuDia.fecha).all()
    total_by_day = _int_dict_from_rows(rows_total)

    rows_consumidas = db.session.query(MenuDia.fecha, func.count(Reserva.id_reserva)) \
        .join(JornadaCocina, Reserva.id_jornada == JornadaCocina.id_jornada) \
        .join(MenuDia, JornadaCocina.id_menu == MenuDia.id_menu) \
        .filter(
            MenuDia.fecha >= start_date,
            MenuDia.fecha <= today,
            Reserva.estado == 'consumida'
        ) \
        .group_by(MenuDia.fecha).all()
    consumidas_by_day = _int_dict_from_rows(rows_consumidas)

    rows_merma_qty = db.session.query(
        MermaIngrediente.fecha,
        func.coalesce(func.sum(MermaIngrediente.cantidad), 0)
    ).filter(
        MermaIngrediente.fecha >= start_date,
        MermaIngrediente.fecha <= today
    ).group_by(MermaIngrediente.fecha).all()
    merma_qty_by_day = _dict_from_rows(rows_merma_qty)

    rows_prepared = db.session.query(
        MenuDia.fecha,
        func.coalesce(func.sum(JornadaCocina.raciones_preparadas), 0)
    ).join(JornadaCocina, JornadaCocina.id_menu == MenuDia.id_menu) \
     .filter(MenuDia.fecha >= start_date, MenuDia.fecha <= today) \
     .group_by(MenuDia.fecha).all()
    prepared_by_day = _int_dict_from_rows(rows_prepared)

    rows_unconsumed = db.session.query(
        MenuDia.fecha,
        func.coalesce(func.sum(JornadaCocina.raciones_disponibles), 0)
    ).join(JornadaCocina, JornadaCocina.id_menu == MenuDia.id_menu) \
     .filter(MenuDia.fecha >= start_date, MenuDia.fecha <= today) \
     .group_by(MenuDia.fecha).all()
    unconsumed_by_day = _int_dict_from_rows(rows_unconsumed)

    consumidas_series = []
    no_consumidas_by_day = []
    merma_percent_series = []
    meta_series = []
    prepared_series = []
    leftover_series = []

    meta = 15.0

    for d in dates:
        t_d = total_by_day.get(d, 0)
        c_d = consumidas_by_day.get(d, 0)
        p_d = prepared_by_day.get(d, 0)
        u_d = unconsumed_by_day.get(d, 0)

        consumidas_series.append(c_d)
        no_consumidas_by_day.append(max(t_d - c_d, 0))
        prepared_series.append(p_d)
        leftover_series.append(u_d)

        m_d = merma_qty_by_day.get(d, 0.0)
        merma_percent_series.append(round((m_d / t_d) * 100, 1) if t_d > 0 else 0.0)
        meta_series.append(meta)

    prepared_total = sum(prepared_series)
    unconsumed_total = sum(leftover_series)

    return {
        'chart_consumidas': {
            'labels': labels,
            'consumidas': consumidas_series,
            'no_consumidas': no_consumidas_by_day
        },
        'chart_merma': {
            'labels': labels,
            'porcentaje': merma_percent_series,
            'meta': meta_series
        },
        'chart_platos': {
            'labels': ['Preparados', 'No consumidos'],
            'data': [prepared_total, unconsumed_total]
        }
    }


def get_inventory_context():
    db, Reserva, JornadaCocina, MenuDia, MermaIngrediente, LoteIngrediente, Ingrediente, Usuario, Rol = _app_objects()

    hoy = date.today()
    limite_vencimiento = hoy + timedelta(days=5)

    ingredientes = (
        Ingrediente.query
        .options(selectinload(Ingrediente.lotes).selectinload(LoteIngrediente.ingrediente))
        .order_by(Ingrediente.nombre.asc())
        .all()
    )

    total_lotes = 0
    lotes_bajos = 0
    total_valor_inventario = 0.0

    for ing in ingredientes:
        ing.lotes.sort(key=lambda l: (l.fecha_vencimiento or date.max, l.id_lote))
        total_lotes += len(ing.lotes)

        for lote in ing.lotes:
            cantidad = float(lote.cantidad_disponible or 0)
            costo = float(lote.costo_unitario or 0)
            total_valor_inventario += cantidad * costo
            if cantidad <= 10:
                lotes_bajos += 1

    lotes_proximos = (
        LoteIngrediente.query
        .options(selectinload(LoteIngrediente.ingrediente))
        .filter(
            LoteIngrediente.fecha_vencimiento >= hoy,
            LoteIngrediente.fecha_vencimiento <= limite_vencimiento
        )
        .order_by(LoteIngrediente.fecha_vencimiento.asc())
        .all()
    )

    for lote in lotes_proximos:
        lote.dias_restantes = (lote.fecha_vencimiento - hoy).days

    return {
        "ingredientes": ingredientes,
        "lotes_proximos": lotes_proximos,
        "total_lotes": total_lotes,
        "lotes_bajos": lotes_bajos,
        "total_valor_inventario": round(total_valor_inventario, 2),
    }


def get_waste_context(start_date, today):
    db, Reserva, JornadaCocina, MenuDia, MermaIngrediente, LoteIngrediente, Ingrediente, Usuario, Rol = _app_objects()
    dates = _date_series(start_date, today)

    rows_qty = db.session.query(
        MermaIngrediente.fecha,
        func.coalesce(func.sum(MermaIngrediente.cantidad), 0)
    ).filter(
        MermaIngrediente.fecha >= start_date,
        MermaIngrediente.fecha <= today
    ).group_by(MermaIngrediente.fecha).all()

    rows_cost = db.session.query(
        MermaIngrediente.fecha,
        func.coalesce(func.sum(MermaIngrediente.costo_perdido), 0)
    ).filter(
        MermaIngrediente.fecha >= start_date,
        MermaIngrediente.fecha <= today
    ).group_by(MermaIngrediente.fecha).all()

    rows_reservas = db.session.query(
        MenuDia.fecha,
        func.count(Reserva.id_reserva)
    ).join(JornadaCocina, Reserva.id_jornada == JornadaCocina.id_jornada) \
     .join(MenuDia, JornadaCocina.id_menu == MenuDia.id_menu) \
     .filter(
         MenuDia.fecha >= start_date,
         MenuDia.fecha <= today
     ) \
     .group_by(MenuDia.fecha).all()

    qty_by_day = _dict_from_rows(rows_qty)
    cost_by_day = _dict_from_rows(rows_cost)
    reservas_by_day = _int_dict_from_rows(rows_reservas)

    mermas_diarias = []
    for d in dates:
        cantidad = float(qty_by_day.get(d, 0.0))
        costo = float(cost_by_day.get(d, 0.0))
        reservas_dia = int(reservas_by_day.get(d, 0))

        porcentaje_merma = round((cantidad / reservas_dia) * 100, 1) if reservas_dia > 0 else 0.0

        mermas_diarias.append({
            "fecha": d.strftime("%Y-%m-%d"),
            "label": d.strftime("%d-%m"),
            "cantidad": round(cantidad, 3),
            "costo": round(costo, 2),
            "porcentaje_merma": porcentaje_merma,
            "reservas_dia": reservas_dia,
        })

    rows_motivo = db.session.query(
        MermaIngrediente.motivo,
        func.coalesce(func.sum(MermaIngrediente.cantidad), 0),
        func.coalesce(func.sum(MermaIngrediente.costo_perdido), 0)
    ).filter(
        MermaIngrediente.fecha >= start_date,
        MermaIngrediente.fecha <= today
    ).group_by(MermaIngrediente.motivo).all()

    mermas_por_motivo = [
        {
            "motivo": motivo or "Sin motivo",
            "cantidad": float(cantidad or 0),
            "costo": float(costo or 0),
        }
        for motivo, cantidad, costo in rows_motivo
    ]
    mermas_por_motivo.sort(key=lambda x: x["costo"], reverse=True)

    mermas_recientes = (
        MermaIngrediente.query
        .filter(
            MermaIngrediente.fecha >= start_date,
            MermaIngrediente.fecha <= today
        )
        .order_by(MermaIngrediente.fecha.desc(), MermaIngrediente.id_merma_ing.desc())
        .limit(30)
        .all()
    )

    total_registros = (
        MermaIngrediente.query
        .filter(
            MermaIngrediente.fecha >= start_date,
            MermaIngrediente.fecha <= today
        )
        .count()
    )

    promedio_diario = round(
        sum(item["cantidad"] for item in mermas_diarias) / len(mermas_diarias),
        3
    ) if mermas_diarias else 0.0

    return {
        "mermas_diarias": mermas_diarias,
        "mermas_por_motivo": mermas_por_motivo,
        "mermas_recientes": mermas_recientes,
        "mermas_registros": total_registros,
        "promedio_merma_diaria": promedio_diario,
    }


def get_users_context():
    db, Reserva, JornadaCocina, MenuDia, MermaIngrediente, LoteIngrediente, Ingrediente, Usuario, Rol = _app_objects()

    usuarios = (
        Usuario.query
        .options(selectinload(Usuario.rol))
        .order_by(Usuario.nombre.asc(), Usuario.apellido.asc())
        .all()
    )

    roles = Rol.query.order_by(Rol.nombre.asc()).all()

    usuarios_activos = [u for u in usuarios if u.estado == "activo"]
    usuarios_bloqueados = [u for u in usuarios if u.estado == "bloqueado"]
    usuarios_atencion = [u for u in usuarios if u.faltas_acumuladas >= 2 or u.estado == "bloqueado"]

    return {
        "usuarios_list": usuarios,
        "roles_list": roles,
        "usuarios_total": len(usuarios),
        "usuarios_activos": len(usuarios_activos),
        "usuarios_bloqueados": len(usuarios_bloqueados),
        "usuarios_atencion": usuarios_atencion,
    }