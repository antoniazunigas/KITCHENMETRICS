import pytest
from app import app as flask_app, db


@pytest.fixture
def app():
    # Configuración de testing
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # BD en memoria
        "WTF_CSRF_ENABLED": False
    })

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()