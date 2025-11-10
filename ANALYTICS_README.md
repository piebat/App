# 📊 Google Analytics Integration - Quick Start

## 🚀 Installazione Rapida

```bash
./setup-analytics.sh
```

## 📝 File Creati

1. **`analytics_dashboard.py`** - Dashboard per visualizzare statistiche Google Analytics
2. **`ga_config.json`** - File di configurazione per Google Analytics
3. **`GOOGLE_ANALYTICS_SETUP.md`** - Guida completa setup
4. **`streamlit-analytics.service`** - Servizio systemd per la dashboard

## 🔧 Configurazione

### 1. Ottieni credenziali Google Analytics:
- Segui la guida dettagliata in `GOOGLE_ANALYTICS_SETUP.md`
- Scarica il file JSON delle credenziali
- Salvalo come `google_analytics_credentials.json`

### 2. Configura ga_config.json:
```json
{
  "ga_measurement_id": "G-XXXXXXXXXX",
  "ga_property_id": "123456789",
  "service_account_file": "google_analytics_credentials.json",
  "tracking_enabled": true
}
```

### 3. Riavvia i servizi:
```bash
sudo systemctl restart streamlit-app
sudo systemctl restart streamlit-analytics
```

## 🌐 Accesso

- **App Principale**: http://localhost:8501
- **Analytics Dashboard**: http://localhost:8502

## 📊 Funzionalità Dashboard

- ✅ Visualizzazione utenti, sessioni, page views
- ✅ Grafici andamento temporale
- ✅ Distribuzione geografica visitatori
- ✅ Sorgenti di traffico
- ✅ Analisi dispositivi (desktop/mobile/tablet)
- ✅ Export dati (CSV)
- ✅ Periodo personalizzabile

## ⚙️ Gestione Servizi

```bash
# Stato
sudo systemctl status streamlit-analytics

# Stop
sudo systemctl stop streamlit-analytics

# Start
sudo systemctl start streamlit-analytics

# Restart
sudo systemctl restart streamlit-analytics

# Log in tempo reale
sudo journalctl -u streamlit-analytics -f
```

## 🔒 Sicurezza

**NON committare questi file:**
- `google_analytics_credentials.json`
- `ga_config.json` (se contiene dati sensibili)

Aggiungi al `.gitignore`:
```
google_analytics_credentials.json
ga_config.json
*.json
```

## ❓ Troubleshooting

### Nessun dato nella dashboard?
1. Verifica che `tracking_enabled: true` in `ga_config.json`
2. Attendi 24-48 ore dopo la prima configurazione
3. Genera traffico visitando l'app principale
4. Verifica i permessi del Service Account in Google Analytics

### Dashboard non si avvia?
```bash
# Controlla i log
sudo journalctl -u streamlit-analytics -n 50

# Verifica dipendenze
source .cer/bin/activate
pip install google-analytics-data plotly openpyxl
```

## 📚 Documentazione Completa

Consulta `GOOGLE_ANALYTICS_SETUP.md` per la guida completa passo-passo.

---

**Versione**: 1.0  
**Last Update**: Novembre 2025
