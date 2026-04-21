def test_admin_solo_admin(client, app):
    with app.app_context():
        from app import db, Usuario, Rol

        # rol funcionario
        rol_func = Rol(nombre="funcionario")
        db.session.add(rol_func)
        db.session.commit()

        user = Usuario(
            id_rol=rol_func.id_rol,
            rut="123",
            nombre="Test",
            apellido="User",
            email="test@test.com",
            contrasena="1234",
            estado="activo"
        )
        db.session.add(user)
        db.session.commit()

    # login como funcionario
    client.post('/login', data={
        'email': 'test@test.com',
        'password': '1234'
    })

    response = client.get('/admin', follow_redirects=True)

    # debería bloquear
    assert b"no autorizado" in response.data.lower() or b"acceso" in response.data.lower()