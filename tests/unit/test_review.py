import pytest
from sqlalchemy.orm import Session
from app.schemas import ReviewCreate
from app.models import DiscountCode, User, Product, Order, OrderStatus, UserRole, Review
from app.services import applica_sconto, checkout, RigaCarrello
from hypothesis import given, strategies as st, settings, HealthCheck

from app.services.review import ricalcola_valutazione_media, ha_acquistato_prodotto, aggiorna_recensione, crea_recensione, elimina_recensione

def test_calcola_media(db_session, make_user, make_product, make_review):
    utente= make_user(saldo=100.0)
    prodotto= make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([utente, prodotto])
    db_session.commit()

    recensione= make_review(user_id=utente.id, product_id=prodotto.id, commento="Buon prodotto", valutazione=4)
    db_session.add(recensione)
    db_session.commit()
    ricalcola_valutazione_media(db_session, prodotto.id)
    db_session.refresh(prodotto)

    assert prodotto.valutazione_media == 4.0

def test_calcola_media_con_recensioni_multiple(db_session, make_user, make_product, make_review):
    utente1= make_user(saldo=100.0)
    utente2= make_user(saldo=100.0)
    prodotto= make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([utente1, utente2, prodotto])
    db_session.commit()

    recensione1= make_review(user_id=utente1.id, product_id=prodotto.id, commento="Buon prodotto", valutazione=4)
    db_session.add(recensione1)
    db_session.commit()
    ricalcola_valutazione_media(db_session, prodotto.id)
    db_session.refresh(prodotto)
    assert prodotto.valutazione_media ==4.0
    recensione2= make_review(user_id=utente2.id, product_id=prodotto.id, commento="pessimo prodotto", valutazione=2)
    db_session.add(recensione2)
    db_session.commit()
    ricalcola_valutazione_media(db_session, prodotto.id)
    db_session.refresh(prodotto)
    assert prodotto.valutazione_media == 3.0
    

def test_crea_recensione_con_successo(db_session: Session, make_user, make_product):
    utente: User = make_user(saldo=100.0)
    prodotto: Product = make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([utente, prodotto])
    db_session.commit()

    ordine = checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=1)], None)
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.commit()

    assert ha_acquistato_prodotto(db_session, utente.id, prodotto.id) is True

    recensione = crea_recensione(db_session, utente.id, prodotto.id, ReviewCreate(commento="Ottimo prodotto!", valutazione=5))
    assert recensione is not None
    assert recensione.valutazione == 5

def test_crea_recensione_senza_acquisto(db_session: Session, make_user, make_product):
    utente: User = make_user(saldo=100.0)
    prodotto: Product = make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([utente, prodotto])
    db_session.commit()

    with pytest.raises(ValueError) as excinfo:
        crea_recensione(db_session, utente.id, prodotto.id, ReviewCreate(commento="Ottimo prodotto!", valutazione=5))
    assert "L'utente non ha acquistato questo prodotto e non può recensirlo." in str(excinfo.value)

def test_crea_recensione_gia_esistente(db_session: Session, make_user, make_product, make_review):
    utente: User = make_user(saldo=100.0)
    prodotto: Product = make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([utente, prodotto])
    db_session.commit()

    ordine = checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=1)], None)
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.commit()

    crea_recensione(db_session, utente.id, prodotto.id, ReviewCreate(commento="Ottimo prodotto!", valutazione=5))

    with pytest.raises(ValueError) as excinfo:
        crea_recensione(db_session, utente.id, prodotto.id, ReviewCreate(commento="Ancora ottimo!", valutazione=4))
    assert "L'utente ha già recensito questo prodotto." in str(excinfo.value)

def test_elimina_recensione_con_successo(db_session: Session, make_user, make_product, make_review):
    utente: User = make_user(saldo=100.0)
    prodotto: Product = make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([utente, prodotto])
    db_session.commit()
    ordine = checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=1)], None)
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.commit()
    recensione = crea_recensione(db_session, utente.id, prodotto.id, ReviewCreate(commento="Ottimo prodotto!", valutazione=5))
    assert recensione is not None
    elimina_recensione(db_session, recensione, utente)
    recensione_eliminata = db_session.get(Review, recensione.id)
    assert recensione_eliminata is None

def test_elimina_recensione_non_autorizzato(db_session: Session, make_user, make_product, make_review):
    utente1: User = make_user(saldo=100.0)
    utente2: User = make_user(saldo=100.0)
    prodotto: Product = make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([utente1, utente2, prodotto])
    db_session.commit()
    ordine = checkout(db_session, utente1, [RigaCarrello(product_id=prodotto.id, quantita=1)], None)
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.commit()
    recensione = crea_recensione(db_session, utente1.id, prodotto.id, ReviewCreate(commento="Ottimo prodotto!", valutazione=5))
    assert recensione is not None

    with pytest.raises(ValueError) as excinfo:
        elimina_recensione(db_session, recensione, utente2)
    assert "L'utente non è autorizzato a eliminare questa recensione." in str(excinfo.value)

def test_elimina_recensione_admin(db_session: Session, make_user, make_product, make_review):
    admin: User = make_user(saldo=100.0, ruolo=UserRole.ADMIN)
    utente: User = make_user(saldo=100.0)
    prodotto: Product = make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([admin, utente, prodotto])
    db_session.commit()
    ordine = checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=1)], None)
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.commit()
    recensione = crea_recensione(db_session, utente.id, prodotto.id, ReviewCreate(commento="Ottimo prodotto!", valutazione=5))
    assert recensione is not None

    elimina_recensione(db_session, recensione, admin)
    recensione_eliminata = db_session.get(Review, recensione.id)
    assert recensione_eliminata is None

def test_aggiorna_recensione_con_successo(db_session: Session, make_user, make_product, make_review):
    utente: User = make_user(saldo=100.0)
    prodotto: Product = make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([utente, prodotto])
    db_session.commit()
    ordine = checkout(db_session, utente, [RigaCarrello(product_id=prodotto.id, quantita=1)], None)
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.commit()
    recensione = crea_recensione(db_session, utente.id, prodotto.id, ReviewCreate(commento="Ottimo prodotto!", valutazione=5))
    assert recensione is not None

    dati_aggiornati = ReviewCreate(commento="Prodotto aggiornato", valutazione=4)
    recensione_aggiornata = aggiorna_recensione(db_session, recensione, dati_aggiornati, utente)
    assert recensione_aggiornata is not None

def test_aggiorna_recensione_non_autorizzato(db_session: Session, make_user, make_product, make_review):
    utente1: User = make_user(saldo=100.0)
    utente2: User = make_user(saldo=100.0)
    prodotto: Product = make_product(prezzo=50.0, giacenza=10)
    db_session.add_all([utente1, utente2, prodotto])
    db_session.commit()
    ordine = checkout(db_session, utente1, [RigaCarrello(product_id=prodotto.id, quantita=1)], None)
    ordine.stato = OrderStatus.CONSEGNATO
    db_session.commit()
    recensione = crea_recensione(db_session, utente1.id, prodotto.id, ReviewCreate(commento="Ottimo prodotto!", valutazione=5))
    assert recensione is not None

    dati_aggiornati = ReviewCreate(commento="Prodotto aggiornato", valutazione=4)
    with pytest.raises(ValueError) as excinfo:
        aggiorna_recensione(db_session, recensione, dati_aggiornati, utente2)
    assert "L'utente non è autorizzato ad aggiornare questa recensione." in str(excinfo.value)