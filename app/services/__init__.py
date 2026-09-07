from app.services.discount import applica_sconto
from app.services.order_state import cambia_stato_ordine, richiedi_rimborso, TRANSIZIONI_VALIDE
from app.services.review import crea_recensione, aggiorna_recensione, elimina_recensione