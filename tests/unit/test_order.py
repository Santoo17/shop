import pytest
from sqlalchemy.orm import Session
from app.models import DiscountCode, User, Product, Order, OrderStatus, UserRole
from app.services import applica_sconto, checkout, RigaCarrello
from hypothesis import given, strategies as st, settings, HealthCheck



def test_acquisto_sconto_nullo(db_session: Session, make_user, make_product):
    utente: User = make_user(saldo=100.0)
    prodotto: Product =  make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([utente, prodotto])
    db_session.commit()
    checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=1)], None)
    order = db_session.query(Order).filter(Order.user_id == utente.id).first()
    assert order is not None
    assert order.stato == OrderStatus.CONFERMATO
    assert order.totale == 50.0
    assert prodotto.giacenza == 9
    assert order.user_id == utente.id
    assert utente.saldo == 50.0

def test_acquisto_sconto(db_session: Session, make_user, make_product, make_discount):
    utente: User = make_user(saldo=100.0)
    prodotto: Product =  make_product(prezzo=50.0, giacenza=10)
    sconto: DiscountCode = make_discount(percentuale=10, attivo=True)
    db_session.add_all([utente, prodotto, sconto])
    db_session.commit()
    checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=1)], sconto.codice)
    order = db_session.query(Order).filter(Order.user_id == utente.id).first()
    assert order is not None
    assert order.stato == OrderStatus.CONFERMATO
    assert order.totale == prodotto.prezzo * 0.9  
    assert prodotto.giacenza == 9
    assert order.user_id == utente.id
    assert utente.saldo == 100.0 - order.totale

def test_acquisto_saldo_insufficiente(db_session: Session, make_user, make_product):
    utente: User = make_user(saldo=30.0)
    prodotto: Product =  make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([utente, prodotto])
    db_session.commit()
    with pytest.raises(ValueError) as excinfo:
        checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=1)], None)
    assert "Saldo insufficiente" in str(excinfo.value)


def test_acquisto_quantita_insufficiente(db_session: Session, make_user, make_product):
    utente: User = make_user(saldo=100.0)
    prodotto: Product =  make_product(prezzo=50.0, giacenza=1)
    db_session.add_all([utente, prodotto])
    db_session.commit()
    with pytest.raises(ValueError) as excinfo:
        checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=2)], None)
    assert "Quantità insufficiente" in str(excinfo.value)

@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=100)
@given(prezzo=st.floats(min_value=0.01, max_value=1000, allow_nan=False), 
       quantita=st.integers(min_value=0, max_value=50))
def test_acquisto_non_porta_giacenza_negativa(db_session: Session, make_user, make_product, prezzo, quantita):
    saldo_iniziale = 10000.0
    giacenza_iniziale = 20
    utente: User = make_user(saldo=saldo_iniziale)
    prodotto: Product =  make_product(prezzo=prezzo, giacenza=  giacenza_iniziale)
    db_session.add_all([utente, prodotto])
    db_session.commit()

    if quantita > giacenza_iniziale:
        with pytest.raises(ValueError) as excinfo:
            checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=quantita)], None)
        assert "Quantità insufficiente" in str(excinfo.value)
    elif utente.saldo < prezzo * quantita:
        with pytest.raises(ValueError) as excinfo:
            checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=quantita)], None)
        assert "Saldo insufficiente" in str(excinfo.value)
    else:
        checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=quantita)], None)
        db_session.refresh(prodotto)
        assert prodotto.giacenza >= 0
        assert prodotto.giacenza == giacenza_iniziale - quantita


