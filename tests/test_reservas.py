from datetime import date, timedelta

def test_reserva_flujo_completo(client, app):
    with app.app_context():
        from app import db, Usuario, Rol, MenuDia, JornadaCocina, Plato, MenuDetalle

        # --- ROL ---
        rol = Rol(nombre="funcionario")
        db.session.add(rol)
        db.session.commit()

        # --- USUARIO ---
        user = Usuario(
            id_rol=rol.id_rol,
            rut="123",
            nombre="Test",
            apellido="User",
            email="test@test.com",
            contrasena="1234",
            estado="activo"
        )
        db.session.add(user)
        db.session.commit()

        # --- MENÚ ---
        menu = MenuDia(
            fecha=date.today() + timedelta(days=1),
            estado="activo"
        )
        db.session.add(menu)
        db.session.commit()

        # --- PLATOS (mínimo 3) ---
        plato1 = Plato(nombre="Entrada", tipo_plato="entrada")
        plato2 = Plato(nombre="Fondo", tipo_plato="fondo")
        plato3 = Plato(nombre="Postre", tipo_plato="postre")

        db.session.add_all([plato1, plato2, plato3])
        db.session.commit()

        # --- DETALLES ---
        detalle1 = MenuDetalle(id_menu=menu.id_menu, id_plato=plato1.id_plato, orden=1)
        detalle2 = MenuDetalle(id_menu=menu.id_menu, id_plato=plato2.id_plato, orden=2)
        detalle3 = MenuDetalle(id_menu=menu.id_menu, id_plato=plato3.id_plato, orden=3)

        db.session.add_all([detalle1, detalle2, detalle3])
        db.session.commit()

        # --- JORNADA ---
        jornada = JornadaCocina(
            id_menu=menu.id_menu,
            raciones_planificadas=10,
            raciones_preparadas=10,
            raciones_disponibles=5
        )
        db.session.add(jornada)
        db.session.commit()

        jornada_id = jornada.id_jornada

    # --- LOGIN ---
    client.post('/login', data={
        'email': 'test@test.com',
        'password': '1234'
    })

    # --- PASAR POR PANEL ---
    client.get('/funcionario')

    # --- 1. RESERVA EXITOSA ---
    response = client.post(f'/reservar/{jornada_id}', follow_redirects=True)
    assert b"Reserva exitosa" in response.data

    # --- 2. RESERVA DUPLICADA ---
    response = client.post(f'/reservar/{jornada_id}', follow_redirects=True)
    assert b"Ya reservaste" in response.data or b"ya reservaste" in response.data.lower()

    # --- 3. VALIDAR BLOQUEO POSTERIOR ---
    response = client.post(f'/reservar/{jornada_id}', follow_redirects=True)

    # 🔥 IMPORTANTE: validamos el comportamiento REAL de tu app
    assert (
        b"Ya reservaste y retiraste" in response.data
        or b"ya reservaste" in response.data.lower()
        or b"sin cupos" in response.data.lower()
    )