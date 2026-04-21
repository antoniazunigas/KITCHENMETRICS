from datetime import date

def test_retirar_desde_funcionario(client, app):
    with app.app_context():
        from app import db, Usuario, Rol, MenuDia, JornadaCocina, Reserva, Plato, MenuDetalle

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

        # --- MENÚ (HOY) ---
        menu = MenuDia(
            fecha=date.today(),
            estado="activo"
        )
        db.session.add(menu)
        db.session.commit()

        # --- PLATOS (IMPORTANTE PARA TEMPLATE) ---
        plato1 = Plato(nombre="Entrada", tipo_plato="entrada")
        plato2 = Plato(nombre="Fondo", tipo_plato="fondo")
        db.session.add_all([plato1, plato2])
        db.session.commit()

        # --- DETALLES ---
        detalle1 = MenuDetalle(id_menu=menu.id_menu, id_plato=plato1.id_plato, orden=1)
        detalle2 = MenuDetalle(id_menu=menu.id_menu, id_plato=plato2.id_plato, orden=2)
        db.session.add_all([detalle1, detalle2])
        db.session.commit()

        # --- JORNADA ---
        jornada = JornadaCocina(
            id_menu=menu.id_menu,
            raciones_planificadas=10,
            raciones_preparadas=10,
            raciones_disponibles=10
        )
        db.session.add(jornada)
        db.session.commit()

        # --- RESERVA ---
        reserva = Reserva(
            id_usuario=user.id_usuario,
            id_jornada=jornada.id_jornada,
            estado="confirmada"
        )
        db.session.add(reserva)
        db.session.commit()

        reserva_id = reserva.id_reserva  # 🔥 FIX IMPORTANTE

    # --- LOGIN ---
    client.post('/login', data={
        'email': 'test@test.com',
        'password': '1234'
    })

    # --- PASAR POR PANEL ---
    client.get('/funcionario')

    # --- 1. RETIRO CORRECTO ---
    response = client.post(f'/retirar/{reserva_id}', data={
        'password_confirmacion': '1234'
    }, follow_redirects=True)

    assert b"Retiro confirmado" in response.data

    # --- 2. PASSWORD INCORRECTA ---
    response = client.post(f'/retirar/{reserva_id}', data={
        'password_confirmacion': 'mala'
    }, follow_redirects=True)

    assert b"Clave incorrecta" in response.data