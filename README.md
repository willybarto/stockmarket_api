# Stock Market API

**Studente:** William Bartolucci

## Tipo di progetto

REST API [file:1]

## Framework utilizzato

Django + Django REST Framework + Simple JWT [file:1]

## Descrizione del progetto

Stock Market API è una REST API back-end che simula una piccola piattaforma di mercato azionario con autenticazione, permessi basati sui ruoli, prezzi storici, gestione dei portafogli e valutazione del portafoglio. Il progetto è stato sviluppato per soddisfare i requisiti della traccia **Stock Market API** dell’esercitazione Back-end PPM 2026, nella quale i dati di borsa possono essere simulati e gli utenti hanno livelli di accesso diversi in base al ruolo.[file:1]

## Funzionalità principali

### Funzionalità pubbliche
- Lista degli asset disponibili.
- Dettaglio di un singolo asset.

### Funzionalità per utenti autenticati
- Login JWT e refresh del token.
- Endpoint profilo utente autenticato (`/api/auth/me/`).
- Creazione, visualizzazione, modifica ed eliminazione dei portafogli.
- Aggiunta di asset a un portafoglio.
- Valutazione aggiornata del portafoglio.

### Funzionalità per utente Basic
- Accesso al quote endpoint con limite giornaliero di 10 richieste.
- Accesso ai prezzi storici fino a 30 giorni.
- Gestione dei propri portafogli.[file:1]

### Funzionalità per utente Pro
- Accesso al quote endpoint con limite giornaliero di 100 richieste.
- Accesso ai prezzi storici fino a 365 giorni.
- Gestione dei propri portafogli con accesso esteso ai dati storici.[file:1]

## Ruoli utente

L’API utilizza un modello utente personalizzato con controllo degli accessi basato sui ruoli. I due ruoli principali previsti dalla traccia sono implementati come `basic` e `pro`, e i permessi sono applicati direttamente nella logica degli endpoint.[file:1]

## Modello relazionale dei dati

Modelli principali:
- `CustomUser`
- `Asset`
- `HistoricalPrice`
- `Portfolio`
- `PortfolioItem`
- `QuoteRequestLog`

Relazioni principali:
- `HistoricalPrice -> Asset` (ForeignKey)
- `Portfolio -> CustomUser` (ForeignKey)
- `PortfolioItem -> Portfolio` (ForeignKey)
- `PortfolioItem -> Asset` (ForeignKey)
- `QuoteRequestLog -> CustomUser` (ForeignKey)

Questa struttura soddisfa il requisito di avere almeno due relazioni reali tra tabelle/risorse esposte dall’API.[file:1]

## Database SQLite incluso

Il repository include un database SQLite pre-popolato:

- `db.sqlite3`

Il database contiene già:
- account demo,
- asset demo,
- prezzi storici simulati,
- portafogli di esempio e relativi elementi.[file:1]

## Account demo

- `admin_demo / admin12345` — amministratore / superuser [file:1]
- `basic_demo / basic12345` — utente basic [file:1]
- `pro_demo / pro12345` — utente pro [file:1]

Queste credenziali sono state create esclusivamente per la valutazione del progetto, come richiesto dalla consegna.[file:1]

## Installazione locale

Clonare il repository:

```bash
git clone <https://github.com/willybarto/stockmarket_api.git>
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

(Opzionale) Ricreare i dati demo:

```bash
python manage.py seed_demo
```

Avviare il server di sviluppo:

```bash
python manage.py runserver
```

URL locale base:

```text
http://127.0.0.1:8000/
```

La consegna richiede che il repository contenga tutto il necessario per eseguire il progetto localmente e che il README spieghi chiaramente i passaggi di installazione e avvio.[file:1]

## Deploy online

Link del deploy:

```text
INSERISCI_QUI_IL_LINK_RENDER_O_RAILWAY
```

La consegna richiede che la REST API sia raggiungibile online e che il link sia riportato chiaramente nel README.[file:1]

## Endpoint principali

| Metodo | URL | Autenticazione | Ruolo consentito | Corpo richiesta | Esempio risposta | Descrizione |
|---|---|---|---|---|---|---|
| POST | `/api/auth/register/` | No | Pubblico | `username, email, password, password_confirm, role` | `{"id":4,"username":"newuser","email":"new@example.com","role":"basic"}` | Registra un nuovo utente. |
| POST | `/api/auth/login/` | No | Pubblico | `username, password` | `{"access":"...","refresh":"..."}` | Restituisce access token e refresh token JWT. |
| POST | `/api/auth/token/refresh/` | No | Pubblico | `refresh` | `{"access":"..."}` | Genera un nuovo access token. |
| GET | `/api/auth/me/` | Sì | Utente autenticato | Nessuno | `{"id":2,"username":"basic_demo","email":"basic@example.com","role":"basic"}` | Restituisce i dati dell’utente autenticato. |
| GET | `/api/assets/` | No | Pubblico | Nessuno | `[{"id":1,"symbol":"AAPL","name":"Apple Inc."}]` | Restituisce la lista degli asset disponibili. |
| GET | `/api/assets/<id>/` | No | Pubblico | Nessuno | `{"id":1,"symbol":"AAPL","name":"Apple Inc.","sector":"Technology"}` | Restituisce il dettaglio di un asset. |
| GET | `/api/assets/<id>/quote/` | Sì | Basic, Pro | Nessuno | `{"asset_id":1,"symbol":"AAPL","close_price":278.28,"daily_limit":10,"requests_today":1,"role":"basic"}` | Restituisce la quotazione più recente dell’asset, con controllo del limite giornaliero. |
| GET | `/api/assets/<id>/history/?days=30` | Sì | Basic, Pro | Nessuno | `{"asset_id":1,"requested_days":30,"max_allowed_days":30,"role":"basic","results":[...]}` | Restituisce i prezzi storici entro il limite consentito dal ruolo. |
| GET | `/api/portfolios/` | Sì | Basic, Pro | Nessuno | `[{"id":1,"name":"Basic Growth Portfolio","owner":"basic_demo","items":[...]}]` | Lista dei portafogli dell’utente autenticato. |
| POST | `/api/portfolios/` | Sì | Basic, Pro | `name` | `{"id":2,"name":"My Test Portfolio"}` | Crea un nuovo portafoglio. |
| GET | `/api/portfolios/<id>/` | Sì | Solo proprietario | Nessuno | `{"id":1,"name":"Basic Growth Portfolio","items":[...]}` | Restituisce il dettaglio di un portafoglio posseduto dall’utente. |
| PUT/PATCH | `/api/portfolios/<id>/` | Sì | Solo proprietario | `name` | `{"id":1,"name":"Portafoglio aggiornato"}` | Aggiorna il nome del portafoglio. |
| DELETE | `/api/portfolios/<id>/` | Sì | Solo proprietario | Nessuno | `204 No Content` | Elimina un portafoglio. |
| POST | `/api/portfolios/<portfolio_id>/items/` | Sì | Solo proprietario | `asset, quantity, average_buy_price` | `{"id":3,"asset":1,"quantity":2,"average_buy_price":"150.00"}` | Aggiunge un asset a un portafoglio. |
| GET | `/api/portfolios/<id>/valuation/` | Sì | Solo proprietario | Nessuno | `{"portfolio_id":1,"portfolio_name":"Basic Growth Portfolio","total_value":2212.23,"items":[...]}` | Calcola il valore di mercato corrente del portafoglio. |
| GET/PUT/DELETE | `/api/portfolio-items/<id>/` | Sì | Solo proprietario | Dipende dal metodo | Oggetto JSON / `204 No Content` | Visualizza, modifica o elimina un singolo elemento del portafoglio. |

La consegna richiede esplicitamente che per una REST API il README contenga una tabella degli endpoint con metodo, URL, autenticazione, ruolo, request body, response example e descrizione.[file:1]

## Workflow di test con HTTPie

La consegna accetta esplicitamente HTTPie come workflow minimo di test per una REST API, purché i comandi siano completi e riproducibili.[file:1]

### 1. Login come utente basic

```bash
http POST http://127.0.0.1:8000/api/auth/login/ username=basic_demo password=basic12345
```

Copiare il valore del campo `access` dalla risposta.

### 2. Salvare il token in una variabile

```bash
TOKEN="INCOLLA_QUI_ACCESS_TOKEN"
```

### 3. Endpoint pubblico: lista asset

```bash
http GET http://127.0.0.1:8000/api/assets/
```

### 4. Endpoint autenticato: quote

```bash
http GET http://127.0.0.1:8000/api/assets/1/quote/ "Authorization: Bearer $TOKEN"
```

### 5. Storico consentito per utente basic

```bash
http GET "http://127.0.0.1:8000/api/assets/1/history/?days=30" "Authorization: Bearer $TOKEN"
```

### 6. Azione vietata per utente basic

```bash
http GET "http://127.0.0.1:8000/api/assets/1/history/?days=365" "Authorization: Bearer $TOKEN"
```

Risultato atteso: `403 Forbidden`, perché un utente basic può accedere a un massimo di 30 giorni di storico.[file:1]

### 7. Lista dei portafogli dell’utente

```bash
http GET http://127.0.0.1:8000/api/portfolios/ "Authorization: Bearer $TOKEN"
```

### 8. Valutazione del portafoglio

```bash
http GET http://127.0.0.1:8000/api/portfolios/1/valuation/ "Authorization: Bearer $TOKEN"
```

### 9. Creazione di un nuovo portafoglio

```bash
http POST http://127.0.0.1:8000/api/portfolios/ "Authorization: Bearer $TOKEN" name="My Test Portfolio"
```

### 10. Aggiunta di un asset al nuovo portafoglio

```bash
http POST http://127.0.0.1:8000/api/portfolios/2/items/ "Authorization: Bearer $TOKEN" asset:=1 quantity:=2 average_buy_price:=150.00
```

### 11. Login come utente pro

```bash
http POST http://127.0.0.1:8000/api/auth/login/ username=pro_demo password=pro12345
```

### 12. Storico esteso per utente pro

```bash
PRO_TOKEN="INCOLLA_QUI_ACCESS_TOKEN_PRO"
http GET "http://127.0.0.1:8000/api/assets/1/history/?days=365" "Authorization: Bearer $PRO_TOKEN"
```

Questo test mostra in modo riproducibile la differenza tra utente `basic` e utente `pro`, che è uno dei requisiti fondamentali della traccia scelta.[file:1]

## Validazione e gestione errori

L’API include:
- validazione tramite serializer per registrazione e dati del portafoglio,
- controllo su quantità e prezzo medio di acquisto,
- risposte JSON coerenti per richieste non valide,
- `403 Forbidden` per violazioni dei permessi di ruolo,
- `404 Not Found` per risorse inesistenti,
- `429 Too Many Requests` quando viene superato il limite giornaliero del quote endpoint.[file:1]

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

La consegna richiede una struttura modulare con almeno due app/moduli coerenti e codice organizzato.[file:1]

## Note finali

- I dati di mercato sono simulati, come consentito esplicitamente dalla traccia del progetto.[file:1]
- Il database incluso permette al docente di testare subito i flussi principali senza dover inserire dati manualmente.[file:1]
- Il progetto può essere ricreato tramite migrazioni e può essere esplorato immediatamente usando il database SQLite incluso.[file:1]