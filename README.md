# Stock Market API

**Studente:** William Bartolucci

## Tipo di progetto

REST API

## Framework utilizzato

Django, Django REST Framework, Simple JWT

## Descrizione del progetto

Stock Market API è una REST API back-end sviluppata con Django REST Framework che simula una piccola piattaforma di mercato azionario. L'applicazione consente agli utenti di registrarsi, autenticarsi tramite JWT, consultare asset e quotazioni, accedere ai prezzi storici con limiti diversi in base al ruolo e gestire uno o più portafogli di investimento.

Il progetto è stato realizzato per la traccia **Stock Market API** dell'esercitazione Back-end PPM 2026. La consegna richiede autenticazione, ruoli, permessi, validazione JSON, documentazione degli endpoint, database demo incluso e workflow di test riproducibile.

## Funzionalità implementate

### Funzionalità pubbliche

- Registrazione di un nuovo utente.
- Login JWT.
- Refresh del token JWT.
- Lista degli asset disponibili.
- Dettaglio di un singolo asset.

### Funzionalità per utenti autenticati

- Endpoint profilo utente autenticato.
- Creazione di portafogli personali.
- Visualizzazione dei propri portafogli.
- Aggiornamento ed eliminazione dei propri portafogli.
- Aggiunta di asset a un portafoglio.
- Visualizzazione, modifica o eliminazione di un singolo portfolio item.
- Valutazione aggiornata del portafoglio con gain/loss in tempo reale.

### Funzionalità per utente Basic

- Accesso all'endpoint quote con rate limiting reale DRF (10 richieste/giorno).
- Accesso ai prezzi storici fino a 30 giorni.
- Filtri storico: range di date (`date_from`, `date_to`) e intervallo (`daily`, `weekly`, `monthly`).
- Gestione dei propri portafogli.

### Funzionalità per utente Pro

- Accesso all'endpoint quote con rate limiting reale DRF (100 richieste/giorno).
- Accesso ai prezzi storici fino a 365 giorni.
- Filtri storico: range di date e intervallo (come per basic, ma con finestra più ampia).
- Gestione dei propri portafogli con accesso esteso allo storico.
- **Watchlist** esclusiva: aggiunta, visualizzazione e rimozione di asset da monitorare.

## Ruoli utente

Il progetto usa un modello utente personalizzato con campo `role`. In fase di registrazione il ruolo deve essere `basic` oppure `pro`, e il serializer valida anche `password` e `password_confirm`.

Ruoli previsti:

- `basic`
- `pro`

Nel database demo è presente anche un superuser amministratore:

- `admin_demo`, con ruolo `pro`, `is_staff=True` e `is_superuser=True`.

## Rate Limiting

Il rate limiting sulle quotazioni è implementato con il throttling nativo di DRF (`SimpleRateThrottle`), non un semplice contatore in database. Il throttle `RoleBasedDailyQuoteThrottle` legge il ruolo dell'utente e applica il rate corretto:

- **Basic**: 10 richieste/giorno
- **Pro**: 100 richieste/giorno

Quando il limite viene superato, DRF restituisce automaticamente `429 Too Many Requests` con header `Retry-After`. Il log delle richieste in database (`QuoteRequestLog`) è mantenuto per tracciabilità.

## Modello dati

Modelli principali del progetto:

- `CustomUser`
- `Asset`
- `HistoricalPrice`
- `Portfolio`
- `PortfolioItem`
- `QuoteRequestLog`
- `Watchlist`

Relazioni principali:

- `HistoricalPrice -> Asset`
- `Portfolio -> CustomUser`
- `PortfolioItem -> Portfolio`
- `PortfolioItem -> Asset`
- `QuoteRequestLog -> CustomUser`
- `Watchlist -> CustomUser`
- `Watchlist -> Asset`

Questa struttura soddisfa il requisito della consegna di esporre almeno due relazioni reali tra risorse e tabelle del database.

## Database SQLite incluso

Il repository include un database SQLite pre-popolato:

- `db.sqlite3`

Il database contiene già dati demo per permettere al docente di testare subito il progetto, come richiesto dalla consegna. In particolare sono già presenti account di test, asset demo, 365 giorni di prezzi storici simulati per ogni asset, portafogli demo, portfolio items già collegati agli utenti e watchlist demo per l'utente pro.

## Account demo

- `admin_demo / admin12345` — amministratore / superuser.
- `basic_demo / basic12345` — utente basic.
- `pro_demo / pro12345` — utente pro.

Queste credenziali sono state create solo per la valutazione del progetto, come richiesto dalle istruzioni della traccia.

## Dati demo già presenti

Nel database sono già presenti almeno questi portafogli:

- `id=1` — `Basic Growth Portfolio`, appartenente a `basic_demo`.
- `id=2` — `Pro Diversified Portfolio`, appartenente a `pro_demo`.

L'utente `pro_demo` ha inoltre 3 asset nella watchlist (AAPL, GOOGL, MSFT).

## Installazione locale

Clonare il repository:

```bash
git clone https://github.com/willybarto/stockmarket_api.git
cd stockmarket_api
```

Creare e attivare un ambiente virtuale:

```bash
python -m venv .venv
source .venv/bin/activate
```

Installare le dipendenze:

```bash
pip install -r requirements.txt
```

Applicare le migrazioni:

```bash
python manage.py migrate
```

Se necessario, popolare o rigenerare i dati demo:

```bash
python manage.py seed_demo
```

Avviare il server locale:

```bash
python manage.py runserver
```

Base URL locale:

```text
http://127.0.0.1:8000/
```

## Management commands

### seed_demo

Popola il database con utenti, asset, storico prezzi, portafogli, portfolio items e watchlist demo:

```bash
python manage.py seed_demo
```

### simulate_prices

Genera variazioni di prezzo simulate (random walk) per tutti gli asset attivi. Utile per aggiungere nuovi dati di storico:

```bash
# Genera il prezzo per oggi
python manage.py simulate_prices

# Genera le ultime 30 giornate
python manage.py simulate_prices --days 30
```

## Test automatici

Il progetto include 35 test automatici con `APITestCase` che coprono:

- Registrazione utente (valida, password mismatch, ruolo invalido, duplicato)
- Login JWT (valido, invalido)
- Endpoint `/me/` (autenticato, non autenticato)
- Lista e dettaglio asset (pubblici)
- Quotazioni (autenticazione, 404)
- Storico prezzi (limiti per ruolo, filtri date, parametro interval, validazione)
- CRUD portfolio completo (creazione, lista, aggiornamento, eliminazione, ownership)
- Valutazione portfolio con gain/loss
- Watchlist (accesso pro, divieto basic, aggiunta, lista, eliminazione, duplicato)

Per eseguire i test:

```bash
python manage.py test
```

Per output dettagliato:

```bash
python manage.py test --verbosity=2
```

## Deploy online

Deploy Render:

[https://stockmarket-api-e7rk.onrender.com](https://stockmarket-api-e7rk.onrender.com)

Dai test effettuati, l'endpoint pubblico `GET /api/assets/` risponde correttamente anche online e restituisce la lista JSON degli asset demo.

## Endpoint principali

| Metodo | URL | Auth | Ruolo | Request body | Esempio risposta | Descrizione |
| --- | --- | --- | --- | --- | --- | --- |
| POST | `/api/auth/register/` | No | Pubblico | `username`, `email`, `password`, `password_confirm`, `role` | `{"id":4,"username":"newuser","email":"new@example.com","role":"basic"}` | Registra un nuovo utente. |
| POST | `/api/auth/login/` | No | Pubblico | `username`, `password` | `{"refresh":"...","access":"..."}` | Restituisce refresh e access token JWT. |
| POST | `/api/auth/token/refresh/` | No | Pubblico | `refresh` | `{"access":"..."}` | Restituisce un nuovo access token. |
| GET | `/api/auth/me/` | Sì | Utente autenticato | Nessuno | `{"id":2,"username":"basic_demo","email":"basic@example.com","role":"basic"}` | Restituisce i dati dell'utente autenticato. |
| GET | `/api/assets/` | No | Pubblico | Nessuno | `[{"id":1,"symbol":"AAPL","name":"Apple Inc."}]` | Lista degli asset disponibili. |
| GET | `/api/assets/<id>/` | No | Pubblico | Nessuno | `{"id":1,"symbol":"AAPL","name":"Apple Inc.","sector":"Technology"}` | Dettaglio di un asset. |
| GET | `/api/assets/<id>/quote/` | Sì | Basic, Pro | Nessuno | `{"asset_id":1,"symbol":"AAPL","close_price":278.28,"daily_limit":10,"requests_today":1,"role":"basic"}` | Quotazione più recente. Rate limiting DRF reale: 10/day basic, 100/day pro. |
| GET | `/api/assets/<id>/history/` | Sì | Basic, Pro | Nessuno | `{"asset_id":1,"interval":"daily","count":30,"results":[...]}` | Storico prezzi con filtri (vedi sotto). |
| GET | `/api/portfolios/` | Sì | Basic, Pro | Nessuno | `[{"id":1,"name":"Basic Growth Portfolio","owner":"basic_demo","items":[...]}]` | Lista dei portafogli dell'utente autenticato. |
| POST | `/api/portfolios/` | Sì | Basic, Pro | `name` | `{"id":3,"name":"My Test Portfolio"}` | Crea un nuovo portafoglio. |
| GET | `/api/portfolios/<id>/` | Sì | Solo proprietario | Nessuno | `{"id":1,"name":"Basic Growth Portfolio","items":[...]}` | Dettaglio di un portafoglio. |
| PUT/PATCH | `/api/portfolios/<id>/` | Sì | Solo proprietario | `name` | `{"id":1,"name":"Portafoglio aggiornato"}` | Aggiorna un portafoglio. |
| DELETE | `/api/portfolios/<id>/` | Sì | Solo proprietario | Nessuno | `204 No Content` | Elimina un portafoglio. |
| POST | `/api/portfolios/<id>/items/` | Sì | Solo proprietario | `asset`, `quantity`, `average_buy_price` | `{"id":6,"asset":5,"asset_symbol":"AMZN","quantity":2,"average_buy_price":"150.00"}` | Aggiunge un asset a un portafoglio. |
| GET/PUT/DELETE | `/api/portfolio-items/<id>/` | Sì | Solo proprietario | Dipende dal metodo | JSON oppure `204 No Content` | Visualizza, modifica o elimina un singolo portfolio item. |
| GET | `/api/portfolios/<id>/valuation/` | Sì | Solo proprietario | Nessuno | `{"total_value":2212.23,"total_gain_loss":512.23,"total_gain_loss_percent":30.14,"items":[...]}` | Valuta il portafoglio con prezzi correnti e calcolo gain/loss. |
| GET | `/api/watchlist/` | Sì | Solo Pro | Nessuno | `[{"id":1,"asset":1,"asset_symbol":"AAPL","latest_price":{...}}]` | Lista degli asset nella watchlist (solo utenti Pro). |
| POST | `/api/watchlist/` | Sì | Solo Pro | `asset` | `{"id":4,"asset":2,"asset_symbol":"GOOGL","latest_price":{...}}` | Aggiunge un asset alla watchlist (solo utenti Pro). |
| DELETE | `/api/watchlist/<id>/` | Sì | Solo Pro | Nessuno | `204 No Content` | Rimuove un asset dalla watchlist (solo utenti Pro). |

### Parametri di filtro per lo storico prezzi

L'endpoint `GET /api/assets/<id>/history/` supporta i seguenti query parameters:

| Parametro | Tipo | Default | Descrizione |
| --- | --- | --- | --- |
| `days` | int | 30 | Ultimi N giorni di storico (max 30 basic, 365 pro). |
| `date_from` | YYYY-MM-DD | — | Data inizio range (alternativo a `days`). |
| `date_to` | YYYY-MM-DD | — | Data fine range (alternativo a `days`). |
| `interval` | string | `daily` | Campionamento: `daily`, `weekly`, `monthly`. |

Esempio con range di date e intervallo settimanale:

```bash
curl -X GET "http://127.0.0.1:8000/api/assets/1/history/?date_from=2026-01-01&date_to=2026-06-01&interval=weekly" \
-H "Authorization: Bearer $PRO_TOKEN"
```

## Gestione errori HTTP

L'API utilizza un exception handler personalizzato che restituisce tutti gli errori in un formato JSON coerente:

```json
{
    "error": true,
    "status_code": 404,
    "detail": "Risorsa non trovata."
}
```

Status code gestiti: 400 (validazione), 401 (autenticazione), 403 (permessi), 404 (non trovato), 405 (metodo non consentito), 429 (rate limit superato).

## Workflow di test con curl

La consegna richiede un workflow di test riproducibile per una REST API, comprensivo di autenticazione, endpoint pubblici, endpoint protetti, operazioni CRUD e almeno un'azione vietata per controllo dei permessi.

### 1. Login come utente basic

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login/" \
-H "Content-Type: application/json" \
-d '{"username":"basic_demo","password":"basic12345"}'
```

Copiare il valore del campo `access` restituito nella risposta JSON.

### 2. Salvare il token access in una variabile

```bash
TOKEN="INCOLLA_QUI_ACCESS_TOKEN"
```

### 3. Chiamare un endpoint pubblico: lista asset

```bash
curl "http://127.0.0.1:8000/api/assets/"
```

Questo endpoint è pubblico e restituisce cinque asset demo: `AAPL`, `GOOGL`, `MSFT`, `TSLA`, `AMZN`.

### 4. Chiamare un endpoint autenticato: profilo utente

```bash
curl -X GET "http://127.0.0.1:8000/api/auth/me/" \
-H "Authorization: Bearer $TOKEN"
```

### 5. Chiamare l'endpoint quote (con rate limiting reale)

```bash
curl -X GET "http://127.0.0.1:8000/api/assets/1/quote/" \
-H "Authorization: Bearer $TOKEN"
```

Il rate limiting è gestito dal throttle DRF nativo. Dopo 10 richieste nello stesso giorno, un utente basic riceverà `429 Too Many Requests`.

### 6. Richiedere lo storico consentito a un utente basic

```bash
curl -X GET "http://127.0.0.1:8000/api/assets/1/history/?days=30" \
-H "Authorization: Bearer $TOKEN"
```

### 7. Storico con filtro per range di date

```bash
curl -X GET "http://127.0.0.1:8000/api/assets/1/history/?date_from=2026-06-01&date_to=2026-06-21&interval=weekly" \
-H "Authorization: Bearer $TOKEN"
```

### 8. Testare un'azione vietata per utente basic: storico esteso

```bash
curl -X GET "http://127.0.0.1:8000/api/assets/1/history/?days=365" \
-H "Authorization: Bearer $TOKEN"
```

Risultato atteso: `403 Forbidden`, perché un utente `basic` non può accedere a 365 giorni di storico.

### 9. Testare un'azione vietata per utente basic: watchlist

```bash
curl -X GET "http://127.0.0.1:8000/api/watchlist/" \
-H "Authorization: Bearer $TOKEN"
```

Risultato atteso: `403 Forbidden` con messaggio "Questa funzionalità è riservata agli utenti Pro."

### 10. Elencare i portafogli dell'utente autenticato

```bash
curl -X GET "http://127.0.0.1:8000/api/portfolios/" \
-H "Authorization: Bearer $TOKEN"
```

### 11. Creare un nuovo portafoglio

```bash
curl -X POST "http://127.0.0.1:8000/api/portfolios/" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{"name":"My Test Portfolio"}'
```

### 12. Aggiungere un asset a un portfolio esistente

```bash
curl -X POST "http://127.0.0.1:8000/api/portfolios/1/items/" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{"asset":5,"quantity":2,"average_buy_price":"150.00"}'
```

### 13. Valutare un portafoglio (con gain/loss)

```bash
curl -X GET "http://127.0.0.1:8000/api/portfolios/1/valuation/" \
-H "Authorization: Bearer $TOKEN"
```

La risposta include `total_value`, `total_cost`, `total_gain_loss` e `total_gain_loss_percent`, calcolati in tempo reale sull'ultimo prezzo simulato.

### 14. Login come utente pro

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login/" \
-H "Content-Type: application/json" \
-d '{"username":"pro_demo","password":"pro12345"}'
```

### 15. Salvare il token pro

```bash
PRO_TOKEN="INCOLLA_QUI_ACCESS_TOKEN_PRO"
```

### 16. Testare lo storico esteso per utente pro

```bash
curl -X GET "http://127.0.0.1:8000/api/assets/1/history/?days=365" \
-H "Authorization: Bearer $PRO_TOKEN"
```

### 17. Testare la watchlist (solo pro)

```bash
# Lista watchlist
curl -X GET "http://127.0.0.1:8000/api/watchlist/" \
-H "Authorization: Bearer $PRO_TOKEN"

# Aggiungere asset alla watchlist
curl -X POST "http://127.0.0.1:8000/api/watchlist/" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $PRO_TOKEN" \
-d '{"asset":4}'

# Rimuovere dalla watchlist (usare l'id restituito dalla POST)
curl -X DELETE "http://127.0.0.1:8000/api/watchlist/4/" \
-H "Authorization: Bearer $PRO_TOKEN"
```

## Workflow di test sul deploy online (Render)

I seguenti comandi curl sono pronti all'uso e possono essere copiati e incollati direttamente nel terminale per testare l'API sul deploy Render senza alcuna modifica.

### 1. Endpoint pubblico: lista asset

```bash
curl -X GET "https://stockmarket-api-e7rk.onrender.com/api/assets/"
```

### 2. Login come utente basic e salvataggio token

```bash
curl -s -X POST "https://stockmarket-api-e7rk.onrender.com/api/auth/login/" \
-H "Content-Type: application/json" \
-d '{"username":"basic_demo","password":"basic12345"}'
```

Copiare il valore del campo `access` e salvarlo in una variabile:

```bash
TOKEN="INCOLLA_QUI_ACCESS_TOKEN"
```

### 3. Profilo utente autenticato

```bash
curl -X GET "https://stockmarket-api-e7rk.onrender.com/api/auth/me/" \
-H "Authorization: Bearer $TOKEN"
```

### 4. Quotazione asset (con rate limiting reale)

```bash
curl -X GET "https://stockmarket-api-e7rk.onrender.com/api/assets/1/quote/" \
-H "Authorization: Bearer $TOKEN"
```

### 5. Storico prezzi (30 giorni, consentito a basic)

```bash
curl -X GET "https://stockmarket-api-e7rk.onrender.com/api/assets/1/history/?days=30" \
-H "Authorization: Bearer $TOKEN"
```

### 6. Azione vietata: storico esteso (365 giorni, vietato a basic)

```bash
curl -X GET "https://stockmarket-api-e7rk.onrender.com/api/assets/1/history/?days=365" \
-H "Authorization: Bearer $TOKEN"
```

Risultato atteso: `403 Forbidden`.

### 7. Azione vietata: watchlist (riservata a utenti Pro)

```bash
curl -X GET "https://stockmarket-api-e7rk.onrender.com/api/watchlist/" \
-H "Authorization: Bearer $TOKEN"
```

Risultato atteso: `403 Forbidden` con messaggio "Questa funzionalità è riservata agli utenti Pro."

### 8. CRUD Portfolio: creazione nuovo portafoglio

```bash
curl -X POST "https://stockmarket-api-e7rk.onrender.com/api/portfolios/" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{"name":"Test Portfolio Online"}'
```

### 9. Lista portafogli dell'utente

```bash
curl -X GET "https://stockmarket-api-e7rk.onrender.com/api/portfolios/" \
-H "Authorization: Bearer $TOKEN"
```

### 10. Valutazione portafoglio con gain/loss

```bash
curl -X GET "https://stockmarket-api-e7rk.onrender.com/api/portfolios/1/valuation/" \
-H "Authorization: Bearer $TOKEN"
```

### 11. Login come utente pro

```bash
curl -s -X POST "https://stockmarket-api-e7rk.onrender.com/api/auth/login/" \
-H "Content-Type: application/json" \
-d '{"username":"pro_demo","password":"pro12345"}'
```

```bash
PRO_TOKEN="INCOLLA_QUI_ACCESS_TOKEN_PRO"
```

### 12. Storico esteso (365 giorni, consentito a pro)

```bash
curl -X GET "https://stockmarket-api-e7rk.onrender.com/api/assets/1/history/?days=365" \
-H "Authorization: Bearer $PRO_TOKEN"
```

### 13. Watchlist (solo pro): lista, aggiunta, rimozione

```bash
# Lista watchlist
curl -X GET "https://stockmarket-api-e7rk.onrender.com/api/watchlist/" \
-H "Authorization: Bearer $PRO_TOKEN"

# Aggiungere asset alla watchlist
curl -X POST "https://stockmarket-api-e7rk.onrender.com/api/watchlist/" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $PRO_TOKEN" \
-d '{"asset":4}'

# Rimuovere dalla watchlist (usare l'id restituito dalla POST)
curl -X DELETE "https://stockmarket-api-e7rk.onrender.com/api/watchlist/4/" \
-H "Authorization: Bearer $PRO_TOKEN"
```

## Validazione e gestione errori

L'API include:

- Validazione del body JSON nei serializer.
- Controllo della conferma password in registrazione.
- Validazione del ruolo in registrazione (`basic` o `pro`).
- Controllo di autenticazione JWT.
- Controllo dei permessi per ruolo.
- Controllo dei permessi di ownership sui portafogli.
- Rate limiting reale DRF sulle quotazioni (throttle nativo con `Retry-After` header).
- Exception handler personalizzato per risposte JSON coerenti su tutti gli errori HTTP.
- Validazione parametri storico (days, date_from, date_to, interval).
- Validazione watchlist (asset attivo, duplicato).

## Struttura del progetto

```text
stockmarket_api/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── users/
│   ├── models.py          # CustomUser con AbstractUser
│   ├── serializers.py      # RegisterSerializer, UserSerializer
│   ├── views.py            # RegisterView, MeView
│   ├── urls.py
│   └── tests.py            # 8 test su auth e permessi
├── market/
│   ├── models.py           # Asset, HistoricalPrice, Portfolio, PortfolioItem, QuoteRequestLog, Watchlist
│   ├── serializers.py      # Serializer per ogni modello
│   ├── views.py            # APIView e generics per tutti gli endpoint
│   ├── urls.py
│   ├── services.py         # Logica di business (quote, valutation con gain/loss)
│   ├── permissions.py      # IsOwner, IsProUser
│   ├── throttles.py        # RoleBasedDailyQuoteThrottle
│   ├── exception_handlers.py  # Handler globale errori JSON
│   ├── admin.py            # Registrazione modelli nel pannello admin
│   ├── tests.py            # 27 test su asset, quote, history, portfolio, watchlist
│   └── management/
│       └── commands/
│           ├── seed_demo.py        # Popola il database demo
│           └── simulate_prices.py  # Genera variazioni di prezzo simulate
├── db.sqlite3
├── requirements.txt
├── manage.py
└── README.md
```

## Requisiti della consegna coperti

Il progetto copre i principali requisiti richiesti dalla traccia REST API:

- Repository GitHub completo.
- Deploy online raggiungibile.
- Database SQLite incluso e pre-popolato.
- Account demo per ruoli diversi.
- Autenticazione JWT.
- Ruoli e permessi applicati negli endpoint.
- Rate limiting reale con DRF throttle.
- Validazione dei dati JSON.
- CRUD completo su risorsa principale (Portfolio).
- Endpoint role-specific (Watchlist solo pro, storico esteso solo pro).
- Endpoint documentati nel README.
- Workflow di test riproducibile.
- Test automatici (35 test con APITestCase).
- Gestione errori HTTP coerente.

## Note finali

- I dati di mercato sono simulati, cosa esplicitamente consentita dalla traccia Stock Market API.
- Il database incluso consente di testare il progetto immediatamente senza creare dati manualmente da zero, come richiesto dalla consegna.
- La documentazione è stata allineata ai test reali eseguiti sul progetto locale e sul deploy.
- Il management command `simulate_prices` permette di generare nuovi dati di prezzo realistici in qualsiasi momento.