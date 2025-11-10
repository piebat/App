import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
from shapely.geometry import Point

# Configurazione pagina
st.set_page_config(layout="wide", page_title="Visualizzatore Shapefile CER")

# Titolo
st.title("Renewable Energy Communities: Monitoring, Optimization and Planning")
st.header("Comunità Energetiche Rinnovabili")

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
    
    # Layout a colonne: mappa (3/4) e dati (1/4)
    col_map, col_data = st.columns([3, 1])
    
    with col_map:
        st.subheader("Mappa")
        
        # Creazione della mappa Folium
        # Calcola il centro della mappa basandosi sul terzo shapefile
        bounds = shape3.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        
        # Crea la mappa
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        # Aggiungi layer terrain
        # folium.TileLayer(
        #     tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}',
        #     attr='Esri',
        #     name='Terrain',
        #     overlay=False,
        #     control=True
        # ).add_to(m)
        
        # Aggiungi anche satellite
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Aggiungi il primo shapefile (autosufficienza energetica) come un unico layer
        if len(shape1) > 0:
            folium.GeoJson(
                shape1,
                name='Autosufficienza Energetica',
                style_function=lambda x: {
                    'fillColor': 'blue',
                    'color': 'darkblue',
                    'weight': 2,
                    'fillOpacity': 0.4
                },
                marker=folium.CircleMarker(radius=6, fill=True, fillColor='blue', fillOpacity=0.7, color='darkblue', weight=2)
            ).add_to(m)
        
        # Aggiungi il secondo shapefile (report_ind_0.5)
        if len(shape2) > 0:
            folium.GeoJson(
                shape2,
                name='Report Ind 0.5',
                style_function=lambda x: {
                    'fillColor': 'green',
                    'color': 'darkgreen',
                    'weight': 2,
                    'fillOpacity': 0.4
                },
                marker=folium.CircleMarker(radius=6, fill=True, fillColor='green', fillOpacity=0.7, color='darkgreen', weight=2)
            ).add_to(m)
        
        # Aggiungi il terzo shapefile (shape da interrogare) con markers
        if len(shape3) > 0:
            # Crea un feature group per i markers
            marker_cluster = folium.FeatureGroup(name='Shape da Interrogare')
            
            for idx, row in shape3.iterrows():
                # Ottieni le coordinate del centroide per il marker
                centroid = row.geometry.centroid
                
                # Crea popup con informazioni
                popup_text = "<br>".join([f"<b>{col}:</b> {row[col]}" for col in shape3.columns if col != 'geometry'])
                
                # Aggiungi marker
                folium.CircleMarker(
                    location=[centroid.y, centroid.x],
                    radius=8,
                    popup=folium.Popup(popup_text, max_width=300),
                    color='darkred',
                    fillColor='red',
                    fillOpacity=0.7,
                    weight=2
                ).add_to(marker_cluster)
                
                # Aggiungi anche la geometria originale
                folium.GeoJson(
                    row.geometry,
                    style_function=lambda x: {
                        'fillColor': 'red',
                        'color': 'darkred',
                        'weight': 2,
                        'fillOpacity': 0.3
                    }
                ).add_to(marker_cluster)
            
            marker_cluster.add_to(m)
        
        # Aggiungi controllo layer
        folium.LayerControl().add_to(m)
        
        # Adatta i bounds della mappa
        m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
        
        # Visualizza la mappa con interattività
        map_data = st_folium(m, width=None, height=600)
    
    with col_data:
        st.subheader("Dati Feature Selezionata")
        
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
                
                for shape, name in [(shape1, "Autosufficienza Energetica"), 
                                   (shape2, "Report Ind 0.5"), 
                                   (shape3, "Shape da Interrogare")]:
                    for idx, row in shape.iterrows():
                        dist = row.geometry.distance(clicked_point)
                        if dist < min_dist:
                            min_dist = dist
                            selected_data = row
                            selected_layer_name = name
                
                if selected_data is not None and min_dist < 0.01:  # Soglia di distanza
                    st.write(f"**Layer:** {selected_layer_name}")
                    st.divider()
                    
                    # Mostra tutti i campi tranne la geometria
                    for col in selected_data.index:
                        if col != 'geometry':
                            st.write(f"**{col}:** {selected_data[col]}")
                else:
                    st.info("Clicca su una feature nella mappa")
            else:
                st.info("Clicca su una feature nella mappa")
        else:
            st.info("Clicca su una feature nella mappa")
            
        # Mostra anche la tabella del terzo shapefile
        st.divider()
        st.write("**Tabella - Shape da Interrogare:**")
        if len(shape3) > 0:
            df_display = shape3.drop(columns=['geometry'])
            st.dataframe(df_display, height=300)
        else:
            st.warning("Nessuna feature trovata")
    
except Exception as e:
    st.error(f"Errore nel caricamento degli shapefile: {str(e)}")
    st.write("Assicurati che i file shapefile siano presenti nella cartella 'Shape CER'")

# Footer con banner loghi
st.divider()
try:
    st.image("loghi.png", use_container_width=True)
except Exception as e:
    st.caption("Logo banner non disponibile")
