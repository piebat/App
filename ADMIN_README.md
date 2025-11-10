# 🔐 Guida Amministratore - Sistema di Configurazione Protetto

## Accesso Amministratore

### Password di Default
- **Password iniziale:** `admin123`
- ⚠️ **IMPORTANTE:** Cambiare la password al primo accesso!

### Come Accedere
1. Aprire l'applicazione Streamlit
2. Nella sidebar, trovare la sezione "🔐 Accesso Amministratore"
3. Inserire la password nel campo "Password:"
4. Cliccare su "🔓 Accedi"

## Funzionalità Amministratore

### 1. Configurazione Campi da Visualizzare
Una volta autenticati, è possibile:
- Selezionare quali campi mostrare per ogni layer:
  - 🔵 Autosufficienza Energetica
  - 🟢 Report Ind 0.5
  - 🔴 Shape da Interrogare
- Salvare la configurazione cliccando "💾 Salva Configurazione"

### 2. Opzioni di Visualizzazione
- **Mostra tutti i campi nei popup**: Controlla se i popup sulla mappa mostrano tutti i campi o solo quelli selezionati
- **Mostra tabella completa**: Attiva/disattiva la visualizzazione della tabella dati

### 3. Cambiare Password
1. Dopo l'accesso, cliccare su "🔑 Cambia Password"
2. Inserire:
   - Password attuale
   - Nuova password (minimo 6 caratteri)
   - Conferma nuova password
3. Cliccare "💾 Salva Nuova Password"

### 4. Logout
- Cliccare su "🔒 Logout" per uscire dalla modalità amministratore
- Le impostazioni salvate rimarranno attive

## File di Configurazione

### `admin_password.json`
- Contiene l'hash SHA-256 della password amministratore
- **Non condividere questo file**
- Backup consigliato dopo il cambio password

### `config_fields.json`
- Contiene la configurazione dei campi da visualizzare
- Può essere modificato manualmente se necessario
- Formato JSON:
```json
{
  "shape1": ["campo1", "campo2", ...],
  "shape2": ["campo1", "campo2", ...],
  "shape3": ["campo1", "campo2", ...]
}
```

## Sicurezza

- La password è salvata come hash SHA-256 (non in chiaro)
- Solo gli amministratori autenticati possono modificare la configurazione
- Gli utenti non autenticati possono solo visualizzare i dati con la configurazione salvata
- La sessione di autenticazione termina quando si ricarica la pagina o si fa logout

## Ripristino Password

Se si perde la password amministratore:

1. Fermare il servizio Streamlit:
```bash
sudo systemctl stop streamlit-app
```

2. Eliminare il file password:
```bash
rm /home/piebat/App/admin_password.json
```

3. Riavviare il servizio:
```bash
sudo systemctl start streamlit-app
```

4. La password tornerà a essere `admin123`

## Note Importanti

- ⚠️ Cambiare SEMPRE la password di default al primo utilizzo
- 💾 Fare backup dei file di configurazione regolarmente
- 🔒 Non condividere la password con utenti non autorizzati
- 📝 Le modifiche alla configurazione sono immediate dopo il salvataggio
