#!/bin/bash

echo "==================================="
echo "Setup Google Analytics Dashboard"
echo "==================================="

# Installa dipendenze
echo ""
echo "📦 Installazione dipendenze..."
source /home/piebat/App/.cer/bin/activate
pip install google-analytics-data plotly openpyxl

# Installa servizio analytics dashboard
echo ""
echo "🔧 Installazione servizio analytics dashboard..."
sudo cp /home/piebat/App/streamlit-analytics.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable streamlit-analytics.service

# Riavvia app principale per applicare modifiche GA tracking
echo ""
echo "🔄 Riavvio app principale..."
sudo systemctl restart streamlit-app

# Avvia analytics dashboard
echo ""
echo "🚀 Avvio analytics dashboard..."
sudo systemctl start streamlit-analytics.service

# Mostra stato
echo ""
echo "📊 Stato servizi:"
sudo systemctl status streamlit-app --no-pager -n 3
echo ""
sudo systemctl status streamlit-analytics --no-pager -n 3

echo ""
echo "==================================="
echo "✅ Setup Completato!"
echo "==================================="
echo ""
echo "📍 App principale: http://0.0.0.0:8501"
echo "📊 Analytics Dashboard: http://0.0.0.0:8502"
echo ""
echo "⚠️  IMPORTANTE: Configura ga_config.json prima di usare la dashboard"
echo "📖 Leggi GOOGLE_ANALYTICS_SETUP.md per istruzioni dettagliate"
echo ""
echo "🔧 Comandi utili:"
echo "  - Stato analytics: sudo systemctl status streamlit-analytics"
echo "  - Stop analytics: sudo systemctl stop streamlit-analytics"
echo "  - Restart analytics: sudo systemctl restart streamlit-analytics"
echo "  - Log analytics: sudo journalctl -u streamlit-analytics -f"
echo ""
