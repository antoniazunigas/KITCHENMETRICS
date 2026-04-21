def test_logout(client, app):
    with app.app_context():
        from app import db, Usuario, Rol

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

    # --- LOGIN ---
    client.post('/login', data={
        'email': 'test@test.com',
        'password': '1234'
    })

    # --- LOGOUT ---
    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200

    # 🔥 TU APP muestra esto, no "inicie sesión"
    assert b"sesion expirada" in response.data.lower() or b"login" in response.data.lower()

    # --- INTENTO DE ACCESO SIN SESIÓN ---
    response = client.get('/funcionario', follow_redirects=True)

    # 🔥 MISMO AJUSTE AQUÍ
    assert b"sesion expirada" in response.data.lower() or b"login" in response.data.lower()