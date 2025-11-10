import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
from shapely.geometry import Point

# Configurazione pagina
st.set_page_config(
    layout="wide", 
    page_title="REC Monitoring & Planning",
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

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
            tiles='CartoDB positron',
            control_scale=True
        )
        
        # Aggiungi layer OpenStreetMap
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='Street Map',
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
                
                # Crea popup con informazioni stilizzate
                popup_html = '<div style="font-family: Arial; min-width: 200px;">'
                popup_html += '<h4 style="color: #dc2626; margin-bottom: 10px;">📍 Feature Info</h4>'
                for col in shape3.columns:
                    if col != 'geometry':
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
                
                for shape, name, color in [(shape1, "Autosufficienza Energetica", "🔵"), 
                                           (shape2, "Report Ind 0.5", "🟢"), 
                                           (shape3, "Shape da Interrogare", "🔴")]:
                    for idx, row in shape.iterrows():
                        dist = row.geometry.distance(clicked_point)
                        if dist < min_dist:
                            min_dist = dist
                            selected_data = row
                            selected_layer_name = name
                            layer_color = color
                
                if selected_data is not None and min_dist < 0.01:  # Soglia di distanza
                    st.markdown(f"#### {layer_color} {selected_layer_name}")
                    st.divider()
                    
                    # Mostra tutti i campi tranne la geometria in un formato migliore
                    for col in selected_data.index:
                        if col != 'geometry':
                            st.markdown(f"**{col}:**")
                            st.write(selected_data[col])
                            st.markdown("---")
                else:
                    st.info("👆 Click on a feature on the map to view details")
            else:
                st.info("👆 Click on a feature on the map to view details")
        else:
            st.info("👆 Click on a feature on the map to view details")
            
        # Mostra anche la tabella del terzo shapefile
        st.divider()
        st.markdown("### 📋 Features Table")
        if len(shape3) > 0:
            df_display = shape3.drop(columns=['geometry'])
            st.dataframe(
                df_display, 
                height=300,
                use_container_width=True,
                hide_index=True
            )
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
