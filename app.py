import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import pandas as pd

# Configurazione pagina
st.set_page_config(layout="wide", page_title="Visualizzatore Shapefile CER")

# Titolo
st.title("Visualizzatore Shapefile - Comunità Energetiche Rinnovabili")

# Caricamento degli shapefile
@st.cache_data
def load_shapefiles():
    shape1 = gpd.read_file("Shape CER/autosufficienza energetica.shp")
    shape2 = gpd.read_file("Shape CER/report_ind_0.5.shp")
    shape3 = gpd.read_file("Shape CER/shape da interrogare.shp")
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
        
        # Informazioni di debug
        st.write(f"Features caricate: Shape1={len(shape1)}, Shape2={len(shape2)}, Shape3={len(shape3)}")
        
        # Creazione della mappa Folium
        # Calcola il centro della mappa basandosi sul terzo shapefile
        bounds = shape3.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        
        st.write(f"Centro mappa: Lat={center_lat:.4f}, Lon={center_lon:.4f}")
        
        # Crea la mappa
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        # Aggiungi il primo shapefile (autosufficienza energetica)
        if len(shape1) > 0:
            # Converti le colonne non-geometriche per il tooltip
            tooltip_fields1 = [col for col in shape1.columns if col != 'geometry']
            folium.GeoJson(
                shape1.__geo_interface__,
                name='Autosufficienza Energetica',
                style_function=lambda x: {
                    'fillColor': 'blue',
                    'color': 'darkblue',
                    'weight': 2,
                    'fillOpacity': 0.4
                },
                tooltip=folium.GeoJsonTooltip(fields=tooltip_fields1, aliases=tooltip_fields1) if tooltip_fields1 else None
            ).add_to(m)
        
        # Aggiungi il secondo shapefile (report_ind_0.5)
        if len(shape2) > 0:
            tooltip_fields2 = [col for col in shape2.columns if col != 'geometry']
            folium.GeoJson(
                shape2.__geo_interface__,
                name='Report Ind 0.5',
                style_function=lambda x: {
                    'fillColor': 'green',
                    'color': 'darkgreen',
                    'weight': 2,
                    'fillOpacity': 0.4
                },
                tooltip=folium.GeoJsonTooltip(fields=tooltip_fields2, aliases=tooltip_fields2) if tooltip_fields2 else None
            ).add_to(m)
        
        # Aggiungi il terzo shapefile (shape da interrogare)
        if len(shape3) > 0:
            tooltip_fields3 = [col for col in shape3.columns if col != 'geometry']
            folium.GeoJson(
                shape3.__geo_interface__,
                name='Shape da Interrogare',
                style_function=lambda x: {
                    'fillColor': 'red',
                    'color': 'darkred',
                    'weight': 2,
                    'fillOpacity': 0.5
                },
                tooltip=folium.GeoJsonTooltip(fields=tooltip_fields3, aliases=tooltip_fields3) if tooltip_fields3 else None
            ).add_to(m)
        
        # Aggiungi controllo layer
        folium.LayerControl().add_to(m)
        
        # Adatta i bounds della mappa
        m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
        
        # Visualizza la mappa
        folium_static(m, width=None, height=600)
    
    with col_data:
        st.subheader("Dati - Shape da Interrogare")
        
        # Selettore per la riga
        if len(shape3) > 0:
            feature_index = st.selectbox(
                "Seleziona feature:",
                range(len(shape3)),
                format_func=lambda x: f"Feature {x+1}"
            )
            
            # Mostra i dati della feature selezionata
            st.write("**Attributi:**")
            feature_data = shape3.iloc[feature_index]
            
            # Mostra tutti i campi tranne la geometria
            for col in shape3.columns:
                if col != 'geometry':
                    st.write(f"**{col}:** {feature_data[col]}")
            
            st.divider()
            
            # Mostra anche una tabella completa scrollabile
            st.write("**Tabella completa:**")
            # Rimuovi la colonna geometry per la visualizzazione
            df_display = shape3.drop(columns=['geometry'])
            st.dataframe(df_display, height=400)
        else:
            st.warning("Nessuna feature trovata nel terzo shapefile")
    
except Exception as e:
    st.error(f"Errore nel caricamento degli shapefile: {str(e)}")
    st.write("Assicurati che i file shapefile siano presenti nella cartella 'Shape CER'")
