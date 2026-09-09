import os
os.environ["TESTING"] = "1"
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.auth import hash_password
from app.core.database import get_db
from app.models import Base, User, Product, DiscountCode, UserRole, Order, OrderStatus, Review

import uuid


engine_test = create_engine(settings.test_database_url)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session")
def setup_database():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def db_session(setup_database):
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def make_user():
    default_password_hash = hash_password("password123")
    def _make_user(saldo=100.0, ruolo=UserRole.STANDARD, **kwargs):
        unique_email = f"user_{uuid.uuid4().hex[:6]}@example.com"
        return User(
            nome="Mario",
            cognome="Rossi",
            email=kwargs.pop("email", unique_email),
            password_digest=default_password_hash,
            saldo=saldo,
            ruolo=ruolo,
            **kwargs
        )
    return _make_user

@pytest.fixture
def make_product():
    def _make_product(prezzo=50.0, giacenza=10, **kwargs):
        return Product(
            nome="Prodotto Test",
            descrizione="Descrizione",
            prezzo=prezzo,
            giacenza=giacenza,
            **kwargs
        )
    return _make_product

@pytest.fixture
def make_discount():
    def _make_discount(codice="TEST10", percentuale=10, attivo=True, **kwargs):
        return DiscountCode(
            codice=codice,
            percentuale=percentuale,
            attivo=attivo,
            **kwargs
        )
    return _make_discount

@pytest.fixture()
def make_order(db_session, make_user,client):
    def _make_order(**kwargs):
        user= make_user()
        db_session.add(user)
        db_session.commit()
        response=client.post("/auth/login", data={
            "username": user.email,
            "password": "password123",
        })
        token = response.json()["access_token"]
        default = {
            "user_id": user.id,
            "totale": 50.0,
            "stato": OrderStatus.CONFERMATO,
            "codice_sconto": None,
        }
        default.update(kwargs)
        return Order(**default), user, token
    return _make_order

@pytest.fixture()
def make_review(db_session):
    def _make_review(**kwargs):
        default = {
            "commento": "Recensione di test",
            "valutazione": 4,
        }
        default.update(kwargs)
        return Review(**default)
    return _make_review

@pytest.fixture()
def admin_token(db_session, client):
    admin = User(
        nome="Admin",
        cognome="Test",
        email="admin@test.com",
        password_digest=hash_password("password123"),
        ruolo=UserRole.ADMIN,
        saldo=0
    )

    db_session.add(admin)
    db_session.commit()

    response =  client.post("/auth/login", data={
        "username": "admin@test.com",
        "password": "password123",
    })
    return response.json()["access_token"]

@pytest.fixture()
def get_user_token(db_session, client):
    def _get_user_token(saldo=1500.0,  ruolo=UserRole.STANDARD):
        email = f"user_{uuid.uuid4().hex[:6]}@test.com"
        user = User(
            nome="User",
            cognome="Test",
            email=email,
            password_digest=hash_password("password123"),
            ruolo=ruolo,
            saldo=saldo
        )

        db_session.add(user)
        db_session.commit()

        response =  client.post("/auth/login", data={
            "username": email,
            "password": "password123",
        })
        return response.json()["access_token"]
    return _get_user_token

