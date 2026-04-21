def test_panel_funcionario_carga(client, app):
    from datetime import date, timedelta

    with app.app_context():
        from app import db, Usuario, Rol, MenuDia, JornadaCocina, Plato, MenuDetalle

        rol = Rol(nombre="funcionario")
        db.session.add(rol)
        db.session.commit()

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

        menu = MenuDia(
            fecha=date.today() + timedelta(days=1),
            estado="activo"
        )
        db.session.add(menu)
        db.session.commit()

        # platos mínimos
        p1 = Plato(nombre="Entrada", tipo_plato="entrada")
        p2 = Plato(nombre="Fondo", tipo_plato="fondo")
        p3 = Plato(nombre="Postre", tipo_plato="postre")

        db.session.add_all([p1, p2, p3])
        db.session.commit()

        d1 = MenuDetalle(id_menu=menu.id_menu, id_plato=p1.id_plato, orden=1)
        d2 = MenuDetalle(id_menu=menu.id_menu, id_plato=p2.id_plato, orden=2)
        d3 = MenuDetalle(id_menu=menu.id_menu, id_plato=p3.id_plato, orden=3)

        db.session.add_all([d1, d2, d3])

        jornada = JornadaCocina(
            id_menu=menu.id_menu,
            raciones_planificadas=10,
            raciones_preparadas=10,
            raciones_disponibles=5
        )
        db.session.add(jornada)
        db.session.commit()

    # login
    client.post('/login', data={
        'email': 'test@test.com',
        'password': '1234'
    })

    response = client.get('/funcionario')

    assert response.status_code == 200
    assert b"Reserva de Almuerzo" in response.data or b"reserva" in response.data.lower()