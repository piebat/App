# 📊 Guida Configurazione Google Analytics

## Overview
Questa guida ti aiuterà a configurare Google Analytics 4 (GA4) per tracciare le visite e visualizzare le statistiche dell'applicazione REC Monitoring.

## Componenti del Sistema

### 1. App Principale (`app.py`)
- Tracking automatico delle visite
- Raccolta dati: page views, utenti, sessioni

### 2. Analytics Dashboard (`analytics_dashboard.py`)
- Visualizzazione metriche in tempo reale
- Grafici interattivi
- Export dati (CSV, Excel)

---

## 🚀 Setup Passo-Passo

### STEP 1: Creare Proprietà Google Analytics 4

1. Vai su [Google Analytics](https://analytics.google.com)
2. Accedi con il tuo account Google
3. Clicca su "Admin" (icona ingranaggio in basso a sinistra)
4. Nella colonna "Account", clicca "Create Account"
5. Nella colonna "Property", clicca "Create Property"
6. Compila i dettagli:
   - **Property name**: REC Monitoring App
   - **Reporting time zone**: (Il tuo fuso orario)
   - **Currency**: EUR
7. Clicca "Next" e completa il wizard
8. **Importante**: Copia e salva il **Measurement ID** (formato: `G-XXXXXXXXXX`)
9. Nella sezione "Data Streams", copia anche il **Property ID** (solo numeri, es: `123456789`)

### STEP 2: Configurare Google Cloud Console

1. Vai su [Google Cloud Console](https://console.cloud.google.com)
2. Crea un nuovo progetto:
   - Nome: `rec-analytics`
   - Clicca "Create"

3. Abilita Google Analytics Data API:
   - Nel menu laterale, vai su "APIs & Services" > "Library"
   - Cerca "Google Analytics Data API"
   - Clicca "Enable"

4. Crea Service Account:
   - Vai su "IAM & Admin" > "Service Accounts"
   - Clicca "Create Service Account"
   - Nome: `analytics-reader`
   - Descrizione: `Service account for reading GA4 data`
   - Clicca "Create and Continue"
   - Role: `Viewer`
   - Clicca "Done"

5. Genera credenziali:
   - Clicca sul Service Account appena creato
   - Vai alla tab "Keys"
   - Clicca "Add Key" > "Create new key"
   - Tipo: JSON
   - Clicca "Create"
   - Il file JSON verrà scaricato automaticamente

6. Rinomina il file scaricato in `google_analytics_credentials.json` e salvalo nella cartella `/home/piebat/App/`

### STEP 3: Assegnare Permessi in Google Analytics

1. Torna su [Google Analytics](https://analytics.google.com)
2. Vai su "Admin"
3. Nella colonna "Property", clicca "Property Access Management"
4. Clicca "+" in alto a destra > "Add users"
5. Inserisci l'email del Service Account (la trovi nel file JSON come `client_email`)
   - Esempio: `analytics-reader@rec-analytics.iam.gserviceaccount.com`
6. Role: **Viewer**
7. Clicca "Add"

### STEP 4: Configurare l'Applicazione

1. Apri il file `/home/piebat/App/ga_config.json`

2. Modifica i valori:
```json
{
  "ga_measurement_id": "G-XXXXXXXXXX",
  "ga_property_id": "123456789",
  "service_account_file": "google_analytics_credentials.json",
  "tracking_enabled": true
}
```

Dove:
- `ga_measurement_id`: Il Measurement ID copiato al STEP 1
- `ga_property_id`: Il Property ID (solo numeri) copiato al STEP 1
- `service_account_file`: Nome del file credenziali (default: `google_analytics_credentials.json`)
- `tracking_enabled`: `true` per abilitare il tracking

3. Salva il file

### STEP 5: Installare Dipendenze

```bash
cd /home/piebat/App
source .cer/bin/activate
pip install google-analytics-data plotly openpyxl
```

### STEP 6: Testare la Configurazione

1. Riavvia l'app principale:
```bash
sudo systemctl restart streamlit-app
```

2. Apri l'app principale in un browser e genera qualche traffico

3. Attendi 24-48 ore per vedere i primi dati in Google Analytics

4. Avvia la dashboard analytics:
```bash
streamlit run analytics_dashboard.py --server.port=8502
```

5. Apri `http://localhost:8502` nel browser

---

## 📊 Utilizzo Analytics Dashboard

### Metriche Disponibili

- **Utenti Totali**: Numero di visitatori unici
- **Sessioni**: Numero di visite
- **Visualizzazioni Pagina**: Numero totale di page views
- **Bounce Rate**: Percentuale di sessioni con una sola pagina vista

### Grafici Interattivi

1. **Andamento Utenti nel Tempo**: Trend giornaliero degli utenti
2. **Distribuzione Geografica**: Top 10 paesi per numero di utenti
3. **Sorgenti di Traffico**: Da dove provengono i visitatori
4. **Dispositivi**: Desktop vs Mobile vs Tablet

### Periodi di Analisi

- Ultimi 7 giorni
- Ultimi 30 giorni
- Ultimi 90 giorni
- Quest'anno
- Personalizzato (seleziona date specifiche)

### Export Dati

- **CSV**: Download dati grezzi in formato CSV
- Tabella dettagliata espandibile con tutti i dati

---

## 🔧 Troubleshooting

### Problema: "File credenziali non trovato"
**Soluzione**: Verifica che il file `google_analytics_credentials.json` sia nella cartella `/home/piebat/App/`

### Problema: "Nessun dato disponibile"
**Soluzioni**:
1. Verifica che il Measurement ID sia corretto in `ga_config.json`
2. Attendi 24-48 ore dopo la prima configurazione
3. Genera traffico visitando l'app principale
4. Verifica i permessi del Service Account in Google Analytics

### Problema: "Google Analytics API non installata"
**Soluzione**: 
```bash
pip install google-analytics-data
```

### Problema: "Permission denied"
**Soluzioni**:
1. Verifica che il Service Account abbia il ruolo "Viewer" in Google Analytics
2. Verifica che l'email del Service Account sia corretta
3. Attendi qualche minuto dopo aver assegnato i permessi

---

## 🔐 Sicurezza

- **NON** condividere il file `google_analytics_credentials.json`
- **NON** committare le credenziali su repository pubblici
- Aggiungi al `.gitignore`:
  ```
  google_analytics_credentials.json
  ga_config.json
  ```

---

## 📝 Note Importanti

1. I dati di Google Analytics hanno un ritardo di 24-48 ore
2. La dashboard usa cache di 1 ora per ottimizzare le performance
3. Clicca "Aggiorna Dati" nella sidebar per forzare l'aggiornamento
4. Il tracking funziona solo se `tracking_enabled: true` in `ga_config.json`

---

## 🆘 Supporto

Per problemi o domande:
1. Verifica questa guida
2. Controlla la [documentazione ufficiale GA4](https://developers.google.com/analytics/devguides/reporting/data/v1)
3. Controlla i log dell'applicazione: `sudo journalctl -u streamlit-app -f`

---

## 📌 Checklist Setup

- [ ] Creata proprietà Google Analytics 4
- [ ] Copiato Measurement ID e Property ID
- [ ] Creato progetto Google Cloud
- [ ] Abilitata Google Analytics Data API
- [ ] Creato Service Account
- [ ] Scaricato file JSON credenziali
- [ ] Assegnato permessi "Viewer" al Service Account in GA
- [ ] Rinominato file credenziali in `google_analytics_credentials.json`
- [ ] Aggiornato `ga_config.json` con ID corretti
- [ ] Installate dipendenze Python
- [ ] Riavviata app principale
- [ ] Testata analytics dashboard
- [ ] Generato traffico di test

---

**Versione**: 1.0  
**Ultimo aggiornamento**: Novembre 2025
