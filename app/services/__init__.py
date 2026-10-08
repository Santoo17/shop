from app.services.discount import applica_sconto, calcola_prezzo_scontato
from app.services.order_state import (
    cambia_stato_ordine,
    richiedi_rimborso,
    TRANSIZIONI_VALIDE,
)
from app.services.review import (
    crea_recensione,
    aggiorna_recensione,
    elimina_recensione,
    calcola_media,
    verifica_puo_aggiornare,
    verifica_puo_eliminare,
    ricalcola_valutazione_media,
)
from app.services.checkout import checkout, aggrega_carrello, RigaCarrello
