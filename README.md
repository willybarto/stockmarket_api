# Stock Market API

**Studente:** William Bartolucci

## Tipo di progetto

REST API

## Framework utilizzato

Django, Django REST Framework, Simple JWT

## Descrizione del progetto

Stock Market API è una REST API back-end sviluppata con Django REST Framework che simula una piccola piattaforma di mercato azionario. L’applicazione consente agli utenti di registrarsi, autenticarsi tramite JWT, consultare asset e quotazioni, accedere ai prezzi storici con limiti diversi in base al ruolo e gestire uno o più portafogli di investimento.

Il progetto è stato realizzato per la traccia **Stock Market API** dell’esercitazione Back-end PPM 2026. La consegna richiede autenticazione, ruoli, permessi, validazione JSON, documentazione degli endpoint, database demo incluso e workflow di test riproducibile.

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
- Valutazione aggiornata del portafoglio.

### Funzionalità per utente Basic

- Accesso all’endpoint quote con limite giornaliero ridotto.
- Accesso ai prezzi storici fino a 30 giorni.
- Gestione dei propri portafogli.

### Funzionalità per utente Pro

- Accesso all’endpoint quote con limite giornaliero più alto.
- Accesso ai prezzi storici fino a 365 giorni.
- Gestione dei propri portafogli con accesso esteso allo storico.

## Ruoli utente

Il progetto usa un modello utente personalizzato con campo `role`. In fase di registrazione il ruolo deve essere `basic` oppure `pro`, e il serializer valida anche `password` e `password_confirm`.

Ruoli previsti:

- `basic`
- `pro`

Nel database demo è presente anche un superuser amministratore:

- `admin_demo`, con ruolo `pro`, `is_staff=True` e `is_superuser=True`.

## Modello dati

Modelli principali del progetto:

- `CustomUser`
- `Asset`
- `HistoricalPrice`
- `Portfolio`
- `PortfolioItem`
- `QuoteRequestLog`

Relazioni principali:

- `HistoricalPrice -> Asset`
- `Portfolio -> CustomUser`
- `PortfolioItem -> Portfolio`
- `PortfolioItem -> Asset`
- `QuoteRequestLog -> CustomUser`

Questa struttura soddisfa il requisito della consegna di esporre almeno due relazioni reali tra risorse e tabelle del database.

## Database SQLite incluso

Il repository include un database SQLite pre-popolato:

- `db.sqlite3`

Il database contiene già dati demo per permettere al docente di testare subito il progetto, come richiesto dalla consegna. In particolare sono già presenti account di test, asset demo, prezzi storici simulati, portafogli demo e portfolio items già collegati agli utenti.

## Account demo

- `admin_demo / admin12345` — amministratore / superuser.
- `basic_demo / basic12345` — utente basic.
- `pro_demo / pro12345` — utente pro.

Queste credenziali sono state create solo per la valutazione del progetto, come richiesto dalle istruzioni della traccia.

## Dati demo già presenti

Nel database sono già presenti almeno questi portafogli:

- `id=1` — `Basic Growth Portfolio`, appartenente a `basic_demo`.
- `id=2` — `Pro Diversified Portfolio`, appartenente a `pro_demo`.

Nei test effettuati si è verificato che nel portfolio `1` erano già presenti alcuni asset, quindi per il comando di creazione del portfolio item nel workflow documentato viene usato `asset=5` (`AMZN`), che è stato effettivamente inserito con successo.

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

## Deploy online

Deploy Render:

[https://stockmarket-api-e7rk.onrender.com](https://stockmarket-api-e7rk.onrender.com) 

Dai test effettuati, l’endpoint pubblico `GET /api/assets/` risponde correttamente anche online e restituisce la lista JSON degli asset demo.

## Endpoint principali

| Metodo | URL | Auth | Ruolo | Request body | Esempio risposta | Descrizione |
| --- | --- | --- | --- | --- | --- | --- |
| POST | `/api/auth/register/` | No | Pubblico | `username`, `email`, `password`, `password_confirm`, `role` | `{"id":4,"username":"newuser","email":"new@example.com","role":"basic"}` | Registra un nuovo utente. |
| POST | `/api/auth/login/` | No | Pubblico | `username`, `password` | `{"refresh":"...","access":"..."}` | Restituisce refresh e access token JWT. |
| POST | `/api/auth/token/refresh/` | No | Pubblico | `refresh` | `{"access":"..."}` | Restituisce un nuovo access token. |
| GET | `/api/auth/me/` | Sì | Utente autenticato | Nessuno | `{"id":2,"username":"basic_demo","email":"basic@example.com","role":"basic"}` | Restituisce i dati dell’utente autenticato. |
| GET | `/api/assets/` | No | Pubblico | Nessuno | `[{"id":1,"symbol":"AAPL","name":"Apple Inc."}]` | Lista degli asset disponibili. |
| GET | `/api/assets/<id>/` | No | Pubblico | Nessuno | `{"id":1,"symbol":"AAPL","name":"Apple Inc.","sector":"Technology"}` | Dettaglio di un asset. |
| GET | `/api/assets/<id>/quote/` | Sì | Basic, Pro | Nessuno | `{"asset_id":1,"symbol":"AAPL","close_price":278.28,"daily_limit":10,"requests_today":1,"role":"basic"}` | Quotazione più recente dell’asset. |
| GET | `/api/assets/<id>/history/?days=30` | Sì | Basic, Pro | Nessuno | `{"asset_id":1,"requested_days":30,"max_allowed_days":30,"role":"basic","results":[...]}` | Storico prezzi entro il limite del ruolo. |
| GET | `/api/portfolios/` | Sì | Basic, Pro | Nessuno | `[{"id":1,"name":"Basic Growth Portfolio","owner":"basic_demo","items":[...]}]` | Lista dei portafogli dell’utente autenticato. |
| POST | `/api/portfolios/` | Sì | Basic, Pro | `name` | `{"id":3,"name":"My Test Portfolio"}` | Crea un nuovo portafoglio. |
| GET | `/api/portfolios/<id>/` | Sì | Solo proprietario | Nessuno | `{"id":1,"name":"Basic Growth Portfolio","items":[...]}` | Dettaglio di un portafoglio. |
| PUT/PATCH | `/api/portfolios/<id>/` | Sì | Solo proprietario | `name` | `{"id":1,"name":"Portafoglio aggiornato"}` | Aggiorna un portafoglio. |
| DELETE | `/api/portfolios/<id>/` | Sì | Solo proprietario | Nessuno | `204 No Content` | Elimina un portafoglio. |
| POST | `/api/portfolios/<portfolio_id>/items/` | Sì | Solo proprietario | `asset`, `quantity`, `average_buy_price` | `{"id":6,"asset":5,"asset_symbol":"AMZN","asset_name":"Amazon.com Inc.","quantity":2,"average_buy_price":"150.00"}` | Aggiunge un asset a un portafoglio. |
| GET | `/api/portfolios/<id>/valuation/` | Sì | Solo proprietario | Nessuno | `{"portfolio_id":1,"portfolio_name":"Basic Growth Portfolio","total_value":2212.23,"items":[...]}` | Valuta il portafoglio con prezzi correnti. |
| GET/PUT/DELETE | `/api/portfolio-items/<id>/` | Sì | Solo proprietario | Dipende dal metodo | JSON oppure `204 No Content` | Visualizza, modifica o elimina un singolo portfolio item. |

## Workflow di test con curl

La consegna richiede un workflow di test riproducibile per una REST API, comprensivo di autenticazione, endpoint pubblici, endpoint protetti, operazioni CRUD e almeno un’azione vietata per controllo dei permessi.

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
curl -H "Authorization: Bearer $TOKEN" \
"http://127.0.0.1:8000/api/assets/"
```

Nei test effettuati questo endpoint ha restituito correttamente cinque asset demo: `AAPL`, `GOOGL`, `MSFT`, `TSLA`, `AMZN`.

### 4. Chiamare un endpoint autenticato: profilo utente

```bash
curl -X GET "http://127.0.0.1:8000/api/auth/me/" \
-H "Authorization: Bearer $TOKEN"
```

### 5. Chiamare l’endpoint quote

```bash
curl -X GET "http://127.0.0.1:8000/api/assets/1/quote/" \
-H "Authorization: Bearer $TOKEN"
```

### 6. Richiedere lo storico consentito a un utente basic

```bash
curl -X GET "http://127.0.0.1:8000/api/assets/1/history/?days=30" \
-H "Authorization: Bearer $TOKEN"
```

### 7. Testare un’azione vietata per utente basic

```bash
curl -X GET "http://127.0.0.1:8000/api/assets/1/history/?days=365" \
-H "Authorization: Bearer $TOKEN"
```

Risultato atteso: richiesta negata, perché un utente `basic` non può accedere a 365 giorni di storico, mentre un utente `pro` sì.

### 8. Elencare i portafogli dell’utente autenticato

```bash
curl -X GET "http://127.0.0.1:8000/api/portfolios/" \
-H "Authorization: Bearer $TOKEN"
```

### 9. Creare un nuovo portafoglio

```bash
curl -X POST "http://127.0.0.1:8000/api/portfolios/" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{"name":"My Test Portfolio"}'
```

### 10. Aggiungere un asset a un portfolio esistente

```bash
curl -X POST "http://127.0.0.1:8000/api/portfolios/1/items/" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-d '{"asset":5,"quantity":2,"average_buy_price":"150.00"}'
```

Questo è il comando corretto verificato nei test reali. È stato usato `asset=5` (`AMZN`) perché nel database demo non era già presente nel portfolio `1`, e la richiesta ha restituito correttamente una creazione valida con risposta JSON `201 Created`.

### 11. Valutare un portafoglio

```bash
curl -X GET "http://127.0.0.1:8000/api/portfolios/1/valuation/" \
-H "Authorization: Bearer $TOKEN"
```

### 12. Login come utente pro

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login/" \
-H "Content-Type: application/json" \
-d '{"username":"pro_demo","password":"pro12345"}'
```

### 13. Salvare il token pro

```bash
PRO_TOKEN="INCOLLA_QUI_ACCESS_TOKEN_PRO"
```

### 14. Testare lo storico esteso per utente pro

```bash
curl -X GET "http://127.0.0.1:8000/api/assets/1/history/?days=365" \
-H "Authorization: Bearer $PRO_TOKEN"
```

Questo test serve a dimostrare in modo riproducibile la differenza di permessi tra ruolo `basic` e ruolo `pro`, che è uno dei requisiti principali della traccia Stock Market API.

## Esempi di test sul deploy online

Gli stessi comandi possono essere eseguiti anche contro il deploy Render, sostituendo la base locale con:

```text
https://stockmarket-api-e7rk.onrender.com
```

Esempio:

```bash
curl -X GET "https://stockmarket-api-e7rk.onrender.com/api/assets/"
```

Dai test effettuati, questo endpoint online restituisce correttamente la lista JSON degli asset demo.

## Validazione e gestione errori

L’API include:

- validazione del body JSON nei serializer,
- controllo della conferma password in registrazione,
- validazione del ruolo in registrazione (`basic` o `pro`),
- controllo di autenticazione JWT,
- controllo dei permessi per ruolo,
- controllo dei permessi di ownership sui portafogli,
- risposte JSON coerenti in caso di errore di validazione o autorizzazione.

Durante i test è emerso anche che l’inserimento duplicato dello stesso asset nello stesso portafoglio può causare un errore di vincolo univoco sul database, perché la coppia `portfolio + asset` deve essere unica.

## Struttura del progetto

```text
stockmarket_api/
├── config/
├── users/
├── market/
├── db.sqlite3
├── requirements.txt
├── manage.py
└── README.md
```

## Requisiti della consegna coperti

Il progetto copre i principali requisiti richiesti dalla traccia REST API:

- repository GitHub completo,
- deploy online raggiungibile,
- database SQLite incluso e pre-popolato,
- account demo per ruoli diversi,
- autenticazione JWT,
- ruoli e permessi applicati negli endpoint,
- validazione dei dati JSON,
- CRUD almeno su una risorsa principale,
- endpoint documentati nel README,
- workflow di test riproducibile.

## Note finali

- I dati di mercato sono simulati, cosa esplicitamente consentita dalla traccia Stock Market API.
- Il database incluso consente di testare il progetto immediatamente senza creare dati manualmente da zero, come richiesto dalla consegna.
- La documentazione è stata allineata ai test reali eseguiti sul progetto locale e sul deploy.