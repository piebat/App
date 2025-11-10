import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Configurazione pagina
st.set_page_config(
    layout="wide",
    page_title="Analytics Dashboard - REC",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Titolo
st.markdown("# 📊 Google Analytics Dashboard")
st.markdown("### Renewable Energy Communities - Traffic Analytics")
st.markdown("---")

# Carica configurazione GA
GA_CONFIG_FILE = "ga_config.json"

def load_ga_config():
    if os.path.exists(GA_CONFIG_FILE):
        with open(GA_CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

ga_config = load_ga_config()

# Funzione per caricare dati da Google Analytics API
@st.cache_data(ttl=3600)  # Cache per 1 ora
def get_analytics_data(property_id, start_date, end_date):
    """
    Recupera dati da Google Analytics Data API (GA4)
    """
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
        
        # Inizializza client
        credentials_file = ga_config.get('service_account_file', 'google_analytics_credentials.json')
        
        if not os.path.exists(credentials_file):
            return None, "File credenziali non trovato"
        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
        client = BetaAnalyticsDataClient()
        
        # Request per report generale
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[
                Dimension(name="date"),
                Dimension(name="country"),
                Dimension(name="sessionSource"),
                Dimension(name="deviceCategory"),
            ],
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="sessions"),
                Metric(name="screenPageViews"),
                Metric(name="averageSessionDuration"),
                Metric(name="bounceRate"),
            ],
        )
        
        response = client.run_report(request)
        
        # Converti in DataFrame
        rows = []
        for row in response.rows:
            rows.append({
                'date': row.dimension_values[0].value,
                'country': row.dimension_values[1].value,
                'source': row.dimension_values[2].value,
                'device': row.dimension_values[3].value,
                'users': int(row.metric_values[0].value),
                'sessions': int(row.metric_values[1].value),
                'pageviews': int(row.metric_values[2].value),
                'avg_duration': float(row.metric_values[3].value),
                'bounce_rate': float(row.metric_values[4].value),
            })
        
        df = pd.DataFrame(rows)
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        
        return df, None
        
    except ImportError:
        return None, "Google Analytics API non installata. Installa: pip install google-analytics-data"
    except Exception as e:
        return None, f"Errore: {str(e)}"

# Sidebar per configurazione
with st.sidebar:
    st.markdown("## ⚙️ Configurazione")
    st.markdown("---")
    
    # Date range selector
    st.markdown("### 📅 Periodo di Analisi")
    date_range = st.selectbox(
        "Seleziona periodo:",
        ["Ultimi 7 giorni", "Ultimi 30 giorni", "Ultimi 90 giorni", "Quest'anno", "Personalizzato"]
    )
    
    today = datetime.now().date()
    
    if date_range == "Ultimi 7 giorni":
        start_date = today - timedelta(days=7)
        end_date = today
    elif date_range == "Ultimi 30 giorni":
        start_date = today - timedelta(days=30)
        end_date = today
    elif date_range == "Ultimi 90 giorni":
        start_date = today - timedelta(days=90)
        end_date = today
    elif date_range == "Quest'anno":
        start_date = datetime(today.year, 1, 1).date()
        end_date = today
    else:  # Personalizzato
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Da:", value=today - timedelta(days=30))
        with col2:
            end_date = st.date_input("A:", value=today)
    
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Aggiorna Dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption(f"**Periodo:** {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
    st.caption(f"**Giorni:** {(end_date - start_date).days}")

# Main content
property_id = ga_config.get('ga_property_id', '')

if not property_id:
    st.error("⚠️ Google Analytics non configurato!")
    st.info("""
    **Per configurare Google Analytics:**
    
    1. **Ottieni il Measurement ID** (G-XXXXXXXXXX) da Google Analytics
    2. **Crea un Service Account** nella Google Cloud Console
    3. **Scarica il file JSON delle credenziali**
    4. **Aggiorna ga_config.json** con:
       - `ga_measurement_id`: Il tuo Measurement ID
       - `ga_property_id`: Il tuo Property ID (solo numeri)
       - `service_account_file`: Path al file credenziali
    5. **Riavvia l'applicazione**
    """)
    
    with st.expander("📖 Guida Dettagliata"):
        st.markdown("""
        ### Setup Google Analytics 4
        
        #### 1. Google Analytics Setup
        - Vai su [Google Analytics](https://analytics.google.com)
        - Crea una proprietà GA4
        - Copia il **Measurement ID** (formato: G-XXXXXXXXXX)
        - Copia il **Property ID** (solo numeri, visibile nelle impostazioni)
        
        #### 2. Google Cloud Console
        - Vai su [Google Cloud Console](https://console.cloud.google.com)
        - Crea un nuovo progetto o seleziona esistente
        - Abilita **Google Analytics Data API**
        - Vai in "IAM & Admin" > "Service Accounts"
        - Crea un nuovo Service Account
        - Scarica il file JSON delle credenziali
        
        #### 3. Permessi
        - In Google Analytics, vai in "Admin" > "Property Access Management"
        - Aggiungi l'email del Service Account come Viewer
        
        #### 4. Configurazione File
        ```json
        {
          "ga_measurement_id": "G-XXXXXXXXXX",
          "ga_property_id": "123456789",
          "service_account_file": "google_analytics_credentials.json"
        }
        ```
        """)
else:
    # Carica i dati
    with st.spinner("Caricamento dati da Google Analytics..."):
        df, error = get_analytics_data(
            property_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
    
    if error:
        st.error(f"❌ {error}")
        st.info("Verifica la configurazione e le credenziali di Google Analytics")
    elif df is None or len(df) == 0:
        st.warning("⚠️ Nessun dato disponibile per il periodo selezionato")
    else:
        # Metriche principali
        st.markdown("## 📈 Metriche Principali")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_users = df['users'].sum()
        total_sessions = df['sessions'].sum()
        total_pageviews = df['pageviews'].sum()
        avg_bounce_rate = df['bounce_rate'].mean()
        
        with col1:
            st.metric("👥 Utenti Totali", f"{total_users:,}")
        with col2:
            st.metric("🔄 Sessioni", f"{total_sessions:,}")
        with col3:
            st.metric("📄 Visualizzazioni Pagina", f"{total_pageviews:,}")
        with col4:
            st.metric("📊 Bounce Rate", f"{avg_bounce_rate:.1%}")
        
        st.markdown("---")
        
        # Grafici
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 📅 Andamento Utenti nel Tempo")
            daily_data = df.groupby('date').agg({
                'users': 'sum',
                'sessions': 'sum',
                'pageviews': 'sum'
            }).reset_index()
            
            fig_timeline = go.Figure()
            fig_timeline.add_trace(go.Scatter(
                x=daily_data['date'],
                y=daily_data['users'],
                name='Utenti',
                line=dict(color='#3b82f6', width=3),
                fill='tonexty'
            ))
            fig_timeline.update_layout(
                height=400,
                hovermode='x unified',
                showlegend=True
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        with col_right:
            st.markdown("### 🌍 Distribuzione Geografica")
            country_data = df.groupby('country')['users'].sum().sort_values(ascending=False).head(10)
            
            fig_countries = px.bar(
                x=country_data.values,
                y=country_data.index,
                orientation='h',
                labels={'x': 'Utenti', 'y': 'Paese'},
                color=country_data.values,
                color_continuous_scale='Blues'
            )
            fig_countries.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_countries, use_container_width=True)
        
        # Seconda riga di grafici
        col_left2, col_right2 = st.columns(2)
        
        with col_left2:
            st.markdown("### 🔗 Sorgenti di Traffico")
            source_data = df.groupby('source')['sessions'].sum().sort_values(ascending=False).head(8)
            
            fig_sources = px.pie(
                values=source_data.values,
                names=source_data.index,
                hole=0.4
            )
            fig_sources.update_layout(height=400)
            st.plotly_chart(fig_sources, use_container_width=True)
        
        with col_right2:
            st.markdown("### 📱 Dispositivi")
            device_data = df.groupby('device')['users'].sum()
            
            fig_devices = px.pie(
                values=device_data.values,
                names=device_data.index,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig_devices.update_layout(height=400)
            st.plotly_chart(fig_devices, use_container_width=True)
        
        st.markdown("---")
        
        # Tabella dati dettagliati
        with st.expander("📋 Dati Dettagliati", expanded=False):
            st.dataframe(
                df.sort_values('date', ascending=False),
                use_container_width=True,
                hide_index=True
            )
        
        # Export dati
        st.markdown("---")
        col_export1, col_export2, col_export3 = st.columns([1, 1, 2])
        
        with col_export1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Scarica CSV",
                data=csv,
                file_name=f'analytics_{start_date}_{end_date}.csv',
                mime='text/csv',
                use_container_width=True
            )
        
        with col_export2:
            excel_buffer = pd.ExcelWriter('temp.xlsx', engine='openpyxl')
            df.to_excel(excel_buffer, index=False)
            excel_buffer.close()
            
        with col_export3:
            st.caption(f"📊 Dataset: {len(df)} righe | Ultimo aggiornamento: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# Footer
st.markdown("---")
st.caption("💡 Google Analytics Dashboard - REC Monitoring System v1.0")
