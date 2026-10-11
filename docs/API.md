# Specifica degli endpoint API

## Registrazione e login

| Metodo | Percorso | Accesso | Corpo | Risposta attesa |
|--------|----------|---------|--------|-----------------|
| POST | `/auth/register` | pubblico | `UserCreate` | 201, `UserRead` |
| POST | `/auth/login` | pubblico | form: `username`, `password` | 200, `Token` (JWT) |

## Prodotti

| Metodo | Percorso | Accesso | Corpo | Risposta attesa |
|--------|----------|---------|--------|-----------------|
| GET | `/products/` | pubblico | | 200, lista di `ProductRead` |
| GET | `/products/{product_id}` | pubblico | | 200, `ProductRead` |
| POST | `/products/` | admin | `ProductCreate` | 201, `ProductRead` |
| PUT | `/products/{product_id}/add_giacenza` | admin | `ProductAddGiacenza` | 200, `ProductRead` |
| PUT | `/products/{product_id}` | admin | `ProductUpdate` | 200, `ProductRead` |
| DELETE | `/products/{product_id}` | admin | | 204 |


## Recensioni

| Metodo | Percorso | Accesso | Corpo | Risposta attesa |
|--------|----------|---------|--------|-----------------|
| GET | `/products/{product_id}/recensioni` | pubblico | | 200, lista di `ReviewRead` |
| POST | `/products/{product_id}/recensioni` | utente loggato | `ReviewCreate` | 201, `ReviewRead` |
| PUT | `/recensioni/{review_id}` | autore | `ReviewUpdate` | 200, `ReviewRead` |
| DELETE | `/recensioni/{review_id}` | autore o admin | | 204 |

## Ordini

| Metodo | Percorso | Accesso | Corpo | Risposta attesa |
|--------|----------|---------|--------|-----------------|
| GET | `/orders` | utente loggato (propri) o admin (tutti) | | 200, lista di `OrderRead` |
| GET | `/orders/{order_id}` | proprietario o admin | | 200, `OrderRead` |
| POST | `/checkout` | utente loggato | `CheckoutRequest` | 201, `OrderRead` |
| POST | `/orders/{order_id}/rimborso` | proprietario o admin | | 200, `OrderRead` |
| PUT | `/orders/{order_id}/status` | admin | `OrderStatusUpdate` | 200, `OrderRead` |


## Utenti

| Metodo | Percorso | Accesso | Corpo | Risposta attesa |
|--------|----------|---------|--------|-----------------|
| GET | `/users/me` | autenticato | | 200, `UserRead` |
| GET | `/users/` | admin | | 200, lista di `UserRead` |
| PUT | `/users/{user_id}` | admin | `AdminUpdate` | 200, `UserRead` |
| PUT | `/users/me` | autenticato | `UserUpdate` | 200, `UserRead` |
| PUT | `/users/{user_id}/add_saldo` | admin | `AdminAddSaldo` | 200, `UserRead` |
| DELETE | `/users/me` | autenticato | | 204 |
| DELETE | `/users/{user_id}` | admin | | 204 |


## Sconti

| Metodo | Percorso | Accesso | Corpo | Risposta attesa |
|--------|----------|---------|--------|-----------------|
| GET | `/discounts/` | pubblico | | 200, lista di `DiscountCodeRead` |
| POST | `/discounts/` | admin | `DiscountCodeCreate` | 201, `DiscountCodeRead` |
| PUT | `/discounts/{discount_id}` | admin | `DiscountCodeUpdate` | 200, `DiscountCodeRead` |
| DELETE | `/discounts/{discount_id}` | admin | | 204 |

## Schemi

Le strutture dei dati usate nelle richieste e nelle risposte, riportate nella colonna corpo, sono descritte in [schema.md](schema.md).