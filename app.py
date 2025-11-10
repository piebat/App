import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
from shapely.geometry import Point
import streamlit.components.v1 as components

# Configurazione pagina
st.set_page_config(
    layout="wide", 
    page_title="REC Monitoring & Planning",
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# Google Analytics Tracking Code
# Crea un file ga_config.json con il tuo Measurement ID: {"ga_measurement_id": "G-XXXXXXXXXX"}
import json
import os

GA_CONFIG_FILE = "ga_config.json"

def load_ga_config():
    if os.path.exists(GA_CONFIG_FILE):
        with open(GA_CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"ga_measurement_id": ""}

ga_config = load_ga_config()
GA_MEASUREMENT_ID = ga_config.get("ga_measurement_id", "")

# Inserisci Google Analytics se configurato
if GA_MEASUREMENT_ID:
    ga_code = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_MEASUREMENT_ID}');
    </script>
    """
    components.html(ga_code, height=0)

# Custom CSS per migliorare l'aspetto
st.markdown("""
    <style>
    /* Header styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-title {
        font-size: 1.5rem;
        color: #059669;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Card styling for data panel */
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Map container */
    .element-container iframe {
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Improve dividers */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(to right, transparent, #667eea, transparent);
    }
    
    /* Better metric display */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #1e3a8a;
    }
    </style>
""", unsafe_allow_html=True)

# Titolo con styling personalizzato
st.markdown('<h1 class="main-title">⚡ Renewable Energy Communities</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Monitoring, Optimization and Planning</p>', unsafe_allow_html=True)

# Sidebar per configurazione
with st.sidebar:
    st.markdown("## ⚙️ Configurazione")
    st.markdown("---")
    
    # File di configurazione per salvare le preferenze e password
    import json
    import os
    import hashlib
    
    CONFIG_FILE = "config_fields.json"
    PASSWORD_FILE = "admin_password.json"
    
    # Funzione per hash della password
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    # Funzione per caricare/creare password admin
    def load_admin_password():
        if os.path.exists(PASSWORD_FILE):
            with open(PASSWORD_FILE, 'r') as f:
                return json.load(f).get('password_hash')
        else:
            # Password di default: "admin123" - Cambiarla al primo accesso!
            default_hash = hash_password("admin123")
            with open(PASSWORD_FILE, 'w') as f:
                json.dump({'password_hash': default_hash}, f)
            return default_hash
    
    # Funzione per salvare nuova password
    def save_admin_password(password):
        with open(PASSWORD_FILE, 'w') as f:
            json.dump({'password_hash': hash_password(password)}, f)
    
    # Funzione per caricare la configurazione
    def load_config():
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    # Funzione per salvare la configurazione
    def save_config(config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    # Inizializza session state per autenticazione
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    if 'show_config' not in st.session_state:
        st.session_state.show_config = False
    
    # Carica password admin e configurazione
    admin_password_hash = load_admin_password()
    config = load_config()
    
    # Area di autenticazione
    st.markdown("### 🔐 Accesso Amministratore")
    
    if not st.session_state.admin_authenticated:
        with st.form("admin_login"):
            password_input = st.text_input("Password:", type="password", key="login_password")
            col_login, col_info = st.columns([2, 1])
            with col_login:
                login_submitted = st.form_submit_button("🔓 Accedi", use_container_width=True)
            # with col_info:
            #     st.caption("Default: admin123")
            
            if login_submitted:
                if hash_password(password_input) == admin_password_hash:
                    st.session_state.admin_authenticated = True
                    st.session_state.show_config = True
                    st.success("✅ Accesso consentito!")
                    st.rerun()
                else:
                    st.error("❌ Password errata!")
    else:
        st.success("✅ Autenticato come Amministratore")
        
        col_logout, col_change_pwd = st.columns(2)
        with col_logout:
            if st.button("🔒 Logout", use_container_width=True):
                st.session_state.admin_authenticated = False
                st.session_state.show_config = False
                st.rerun()
        with col_change_pwd:
            if st.button("🔑 Cambia Password", use_container_width=True):
                st.session_state.show_change_password = True
        
        # Form per cambiare password
        if st.session_state.get('show_change_password', False):
            st.markdown("---")
            st.markdown("#### 🔑 Cambia Password")
            with st.form("change_password"):
                old_pwd = st.text_input("Password attuale:", type="password")
                new_pwd = st.text_input("Nuova password:", type="password")
                confirm_pwd = st.text_input("Conferma nuova password:", type="password")
                
                if st.form_submit_button("💾 Salva Nuova Password"):
                    if hash_password(old_pwd) != admin_password_hash:
                        st.error("❌ Password attuale errata!")
                    elif new_pwd != confirm_pwd:
                        st.error("❌ Le password non corrispondono!")
                    elif len(new_pwd) < 6:
                        st.error("❌ La password deve essere lunga almeno 6 caratteri!")
                    else:
                        save_admin_password(new_pwd)
                        st.success("✅ Password cambiata con successo!")
                        st.session_state.show_change_password = False
                        st.rerun()
        
        st.markdown("---")
    
    st.markdown("### 📋 Campi da Visualizzare")
    st.caption("Seleziona i campi da mostrare nei dettagli delle feature")

# Caricamento degli shapefile
@st.cache_data
def load_shapefiles():
    try:
        # Usa il driver 'ESRI Shapefile' e ignora geometrie invalide
        shape1 = gpd.read_file("Shape CER/autosufficienza energetica.shp", driver='ESRI Shapefile', ignore_geometry=False)
        shape2 = gpd.read_file("Shape CER/report_ind_0.5.shp", driver='ESRI Shapefile', ignore_geometry=False)
        shape3 = gpd.read_file("Shape CER/shape da interrogare.shp", driver='ESRI Shapefile', ignore_geometry=False)
    except Exception as e:
        # Se fallisce, prova con engine alternativo
        import fiona
        shape1 = gpd.read_file("Shape CER/autosufficienza energetica.shp", engine='fiona')
        shape2 = gpd.read_file("Shape CER/report_ind_0.5.shp", engine='fiona')
        shape3 = gpd.read_file("Shape CER/shape da interrogare.shp", engine='fiona')
    
    # Rimuovi eventuali geometrie None o invalide
    shape1 = shape1[shape1.geometry.notnull()]
    shape2 = shape2[shape2.geometry.notnull()]
    shape3 = shape3[shape3.geometry.notnull()]
    
    # Valida e ripara geometrie se necessario
    if not shape1.is_valid.all():
        shape1['geometry'] = shape1.geometry.buffer(0)
    if not shape2.is_valid.all():
        shape2['geometry'] = shape2.geometry.buffer(0)
    if not shape3.is_valid.all():
        shape3['geometry'] = shape3.geometry.buffer(0)
    
    return shape1, shape2, shape3

try:
    shape1, shape2, shape3 = load_shapefiles()
    
    # Converti tutti gli shapefile a WGS84 (EPSG:4326) per Folium
    shape1 = shape1.to_crs(epsg=4326)
    shape2 = shape2.to_crs(epsg=4326)
    shape3 = shape3.to_crs(epsg=4326)
    
    # Configurazione campi nella sidebar
    with st.sidebar:
        # Ottieni tutti i campi disponibili (escludi geometry)
        all_fields_shape1 = [col for col in shape1.columns if col != 'geometry']
        all_fields_shape2 = [col for col in shape2.columns if col != 'geometry']
        all_fields_shape3 = [col for col in shape3.columns if col != 'geometry']
        
        # Mostra i controlli solo se autenticato
        if st.session_state.admin_authenticated:
            st.markdown("---")
            
            # Configurazione per ogni layer
            st.markdown("#### 🔵 Autosufficienza Energetica")
            selected_fields_shape1 = st.multiselect(
                "Campi da visualizzare:",
                options=all_fields_shape1,
                default=config.get('shape1', all_fields_shape1[:5] if len(all_fields_shape1) > 5 else all_fields_shape1),
                key="fields_shape1",
                disabled=False
            )
            
            st.markdown("#### 🟢 Report Ind 0.5")
            selected_fields_shape2 = st.multiselect(
                "Campi da visualizzare:",
                options=all_fields_shape2,
                default=config.get('shape2', all_fields_shape2[:5] if len(all_fields_shape2) > 5 else all_fields_shape2),
                key="fields_shape2",
                disabled=False
            )
            
            st.markdown("#### 🔴 Shape da Interrogare")
            selected_fields_shape3 = st.multiselect(
                "Campi da visualizzare:",
                options=all_fields_shape3,
                default=config.get('shape3', all_fields_shape3[:5] if len(all_fields_shape3) > 5 else all_fields_shape3),
                key="fields_shape3",
                disabled=False
            )
            
            # Pulsante per salvare la configurazione
            if st.button("💾 Salva Configurazione", use_container_width=True):
                new_config = {
                    'shape1': selected_fields_shape1,
                    'shape2': selected_fields_shape2,
                    'shape3': selected_fields_shape3
                }
                save_config(new_config)
                st.success("✅ Configurazione salvata!")
            
            st.markdown("---")
            st.markdown("### 🎨 Opzioni Visualizzazione")
            
            show_all_in_popup = st.checkbox("Mostra tutti i campi nei popup", value=True)
            show_table = st.checkbox("Mostra tabella completa", value=True)
        else:
            # Se non autenticato, usa la configurazione salvata (sola lettura)
            st.info("🔒 Accedi come amministratore per modificare la configurazione")
            selected_fields_shape1 = config.get('shape1', all_fields_shape1[:5] if len(all_fields_shape1) > 5 else all_fields_shape1)
            selected_fields_shape2 = config.get('shape2', all_fields_shape2[:5] if len(all_fields_shape2) > 5 else all_fields_shape2)
            selected_fields_shape3 = config.get('shape3', all_fields_shape3[:5] if len(all_fields_shape3) > 5 else all_fields_shape3)
            show_all_in_popup = True
            show_table = True
            
            # Mostra configurazione attuale
            st.markdown("---")
            st.markdown("### 📊 Configurazione Attuale")
            st.caption(f"🔵 Autosufficienza: {len(selected_fields_shape1)} campi")
            st.caption(f"🟢 Report Ind 0.5: {len(selected_fields_shape2)} campi")
            st.caption(f"🔴 Da Interrogare: {len(selected_fields_shape3)} campi")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔵 Autosufficienza", len(shape1), help="Numero di features nel layer Autosufficienza Energetica")
    with col2:
        st.metric("🟢 Report Ind 0.5", len(shape2), help="Numero di features nel layer Report")
    with col3:
        st.metric("🔴 Da Interrogare", len(shape3), help="Numero di features nel layer Shape da Interrogare")
    with col4:
        st.metric("📊 Totale Features", len(shape1) + len(shape2) + len(shape3))
    
    st.markdown("---")
    
    # Layout a colonne: mappa (3/4) e dati (1/4)
    col_map, col_data = st.columns([3, 1], gap="large")
    
    with col_map:
        st.markdown("### 🗺️ Interactive Map")
        
        # Creazione della mappa Folium
        # Calcola il centro della mappa basandosi sul terzo shapefile
        bounds = shape3.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        
        # Crea la mappa con stile migliorato
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='OpenStreetMap',
            control_scale=True
        )
        
        # Aggiungi layer CartoDB Positron
        folium.TileLayer(
            tiles='CartoDB positron',
            name='CartoDB Positron',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Aggiungi layer satellite
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Aggiungi il primo shapefile (autosufficienza energetica) con styling migliorato
        if len(shape1) > 0:
            folium.GeoJson(
                shape1,
                name='🔵 Autosufficienza Energetica',
                style_function=lambda x: {
                    'fillColor': '#3b82f6',
                    'color': '#1e40af',
                    'weight': 2.5,
                    'fillOpacity': 0.5,
                    'dashArray': '5, 5'
                },
                marker=folium.CircleMarker(radius=7, fill=True, fillColor='#3b82f6', fillOpacity=0.8, color='#1e40af', weight=2)
            ).add_to(m)
        
        # Aggiungi il secondo shapefile (report_ind_0.5) con styling migliorato
        if len(shape2) > 0:
            folium.GeoJson(
                shape2,
                name='🟢 Report Ind 0.5',
                style_function=lambda x: {
                    'fillColor': '#10b981',
                    'color': '#059669',
                    'weight': 2.5,
                    'fillOpacity': 0.5,
                    'dashArray': '5, 5'
                },
                marker=folium.CircleMarker(radius=7, fill=True, fillColor='#10b981', fillOpacity=0.8, color='#059669', weight=2)
            ).add_to(m)
        
        # Aggiungi il terzo shapefile (shape da interrogare) con markers migliorati
        if len(shape3) > 0:
            # Crea un feature group per i markers
            marker_cluster = folium.FeatureGroup(name='🔴 Shape da Interrogare')
            
            for idx, row in shape3.iterrows():
                # Ottieni le coordinate del centroide per il marker
                centroid = row.geometry.centroid
                
                # Crea popup con informazioni stilizzate - usa i campi configurati o tutti
                popup_html = '<div style="font-family: Arial; min-width: 200px;">'
                popup_html += '<h4 style="color: #dc2626; margin-bottom: 10px;">📍 Feature Info</h4>'
                
                fields_to_show = selected_fields_shape3 if selected_fields_shape3 and not show_all_in_popup else [col for col in shape3.columns if col != 'geometry']
                
                for col in fields_to_show:
                    if col in row.index and col != 'geometry':
                        popup_html += f'<p style="margin: 5px 0;"><b>{col}:</b> {row[col]}</p>'
                popup_html += '</div>'
                
                # Aggiungi marker con icona personalizzata
                folium.CircleMarker(
                    location=[centroid.y, centroid.x],
                    radius=10,
                    popup=folium.Popup(popup_html, max_width=350),
                    tooltip=f"Click for details",
                    color='#991b1b',
                    fillColor='#ef4444',
                    fillOpacity=0.8,
                    weight=3
                ).add_to(marker_cluster)
                
                # Aggiungi anche la geometria originale
                folium.GeoJson(
                    row.geometry,
                    style_function=lambda x: {
                        'fillColor': '#f87171',
                        'color': '#991b1b',
                        'weight': 2.5,
                        'fillOpacity': 0.4
                    }
                ).add_to(marker_cluster)
            
            marker_cluster.add_to(m)
        
        # Aggiungi controllo layer con fullscreen
        folium.LayerControl(position='topright', collapsed=False).add_to(m)
        
        # Aggiungi plugin fullscreen
        from folium.plugins import Fullscreen
        Fullscreen(position='topleft').add_to(m)
        
        # Adatta i bounds della mappa
        m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
        
        # Visualizza la mappa con interattività
        map_data = st_folium(m, width=None, height=650, returned_objects=["last_object_clicked"])
    
    with col_data:
        st.markdown("### 📊 Feature Details")
        
        # Mostra i dati basati sul click sulla mappa
        if map_data and map_data.get('last_object_clicked'):
            clicked = map_data['last_object_clicked']
            
            # Cerca la feature più vicina al punto cliccato
            clicked_lat = clicked.get('lat')
            clicked_lng = clicked.get('lng')
            
            if clicked_lat and clicked_lng:
                clicked_point = Point(clicked_lng, clicked_lat)
                
                # Cerca in tutti e tre gli shapefile
                min_dist = float('inf')
                selected_data = None
                selected_layer_name = None
                layer_color = None
                selected_fields = None
                
                for shape, name, color, fields in [(shape1, "Autosufficienza Energetica", "🔵", selected_fields_shape1), 
                                                    (shape2, "Report Ind 0.5", "🟢", selected_fields_shape2), 
                                                    (shape3, "Shape da Interrogare", "🔴", selected_fields_shape3)]:
                    for idx, row in shape.iterrows():
                        dist = row.geometry.distance(clicked_point)
                        if dist < min_dist:
                            min_dist = dist
                            selected_data = row
                            selected_layer_name = name
                            layer_color = color
                            selected_fields = fields
                
                if selected_data is not None and min_dist < 0.01:  # Soglia di distanza
                    st.markdown(f"#### {layer_color} {selected_layer_name}")
                    st.divider()
                    
                    # Mostra solo i campi configurati
                    if selected_fields:
                        for col in selected_fields:
                            if col in selected_data.index and col != 'geometry':
                                st.markdown(f"**{col}:**")
                                st.write(selected_data[col])
                                st.markdown("---")
                    else:
                        st.warning("⚠️ Nessun campo selezionato per la visualizzazione")
                        st.caption("Usa la sidebar per selezionare i campi da visualizzare")
                else:
                    st.info("👆 Click on a feature on the map to view details")
            else:
                st.info("👆 Click on a feature on the map to view details")
        else:
            st.info("👆 Click on a feature on the map to view details")
            
        # Mostra anche la tabella del terzo shapefile
        if show_table:
            st.divider()
            with st.expander("📋 Features Table", expanded=False):
                if len(shape3) > 0:
                    # Mostra solo le colonne selezionate se configurate
                    if selected_fields_shape3:
                        cols_to_show = [col for col in selected_fields_shape3 if col in shape3.columns]
                        df_display = shape3[cols_to_show]
                    else:
                        df_display = shape3.drop(columns=['geometry'])
                    
                    st.dataframe(
                        df_display, 
                        height=300,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Mostra info su quante colonne sono visualizzate
                    st.caption(f"📊 Visualizzate {len(df_display.columns)} colonne su {len(shape3.columns)-1} disponibili")
                else:
                    st.warning("⚠️ No features found")
    
except Exception as e:
    st.error(f"❌ Error loading shapefiles: {str(e)}")
    st.info("Please ensure shapefile data is available in the 'Shape CER' folder")

# Footer con banner loghi e info
st.markdown("---")
st.markdown("### 🏛️ Project Partners")
try:
    st.image("loghi.png", use_container_width=True)
except Exception as e:
    st.caption("💡 Logo banner not available")

# Info footer
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.markdown("**📍 Location**")
    st.caption("Renewable Energy Communities")
with col_f2:
    st.markdown("**📅 Last Updated**")
    st.caption("November 2025")
with col_f3:
    st.markdown("**🔄 Version**")
    st.caption("v1.0")
