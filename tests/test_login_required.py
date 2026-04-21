def test_acceso_sin_login_redirige(client):
    response = client.get('/admin', follow_redirects=True)

    assert response.status_code == 200
    assert b"Sesion expirada" in response.data or b"Sesi" in response.data