def test_auth_login(client, app):
    with app.app_context():
        from app import db, Usuario, Rol

        # --- CREAR ROL ---
        rol = Rol(nombre="admin")
        db.session.add(rol)
        db.session.commit()

        # --- CREAR USUARIO ---
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

    # --- 1. LOGIN CORRECTO ---
    response = client.post('/login', data={
        'email': 'test@test.com',
        'password': '1234'
    })

    assert response.status_code == 302
    assert "/admin/dashboard/principal" in response.location

    # --- 2. CONTRASEÑA INCORRECTA ---
    response = client.post('/login', data={
        'email': 'test@test.com',
        'password': 'mala'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"incorrectas" in response.data.lower()

    # --- 3. USUARIO NO EXISTE ---
    response = client.post('/login', data={
        'email': 'noexiste@test.com',
        'password': '1234'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"incorrectas" in response.data.lower()