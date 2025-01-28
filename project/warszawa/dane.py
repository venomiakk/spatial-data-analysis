import folium
from folium.plugins import HeatMap
import geopandas as gpd

# Wczytanie danych GeoJSON lub Shapefile
shapefile = 'Stacje rowerowe VETURILO - Warszawa\\VETURILO_Warszawa.shp'  # Ścieżka do pliku z danymi stacji Veturilo
shapefile2 = 'Trasy rowerowe Warszawa\\TrasyRowerowe_Warszawa.shp'  # Ścieżka do pliku z danymi o drogach rowerowych

data = gpd.read_file(shapefile)
data2 = gpd.read_file(shapefile2)

# Przekształcenie układu współrzędnych na WGS84 (EPSG:4326), jeśli to konieczne
data = data.to_crs(epsg=4326)
data2 = data2.to_crs(epsg=4326)

# Przygotowanie danych do mapy ciepła
heat_data = [
    [row.geometry.y, row.geometry.x, row["Ilość st"]]
    for _, row in data.iterrows()
    if row["Ilość st"] > 0  # Uwzględniamy tylko punkty z dodatnią ilością rowerów
]

# Tworzenie mapy Folium
m = folium.Map(location=[52.2297, 21.0122], zoom_start=12)  # Centrum Warszawy

# Dodanie warstwy mapy ciepła
layer_2 = folium.FeatureGroup(name="Mapa ciepła", show=False)
HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(layer_2)
layer_2.add_to(m)

# Dodanie warstwy z markerami (wskaźnikami) z informacjami o stacjach
marker_layer = folium.FeatureGroup(name="Stacje Veturilo", show=False)  # Warstwa markerów (wyłączona na początku)

for _, row in data.iterrows():
    if row["Ilość st"] > 0:
        # Dodanie markera w miejscu stacji
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=f"Lokalizacja: {row['Lokalizacj']}<br>Ilość rowerów: {row['Ilość st']}",
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(marker_layer)

# Zastąpienie NaN w 'MATE_NAWIE' na 'inny'
data2['MATE_NAWIE'] = data2['MATE_NAWIE'].fillna('inny')

# Wyświetlenie unikalnych typów nawierzchni w kolumnie 'MATE_NAWIE'
unique_surface_types = data2['MATE_NAWIE'].unique()
print("Unikalne typy nawierzchni:", unique_surface_types)

# Przydzielenie kolorów do typów nawierzchni
surface_colors = {
    'kostka prefabrykowana': 'blue',
    'masa bitumiczna': 'black',
    'grunt naturalny': 'brown',
    'kostka kamienna': 'gray',
    'płyty betonowe': 'green',
    'beton': 'red',
    'inny': 'yellow',
    'bruk': 'orange',
}

# Tworzenie warstw dla każdego unikalnego typu nawierzchni
surface_layers = {}  # Słownik do przechowywania warstw

# Tworzymy warstwę dla nawierzchni "inny" (dla None)
surface_layers['inny'] = folium.FeatureGroup(name="Nawierzchnia: inny", show=False)

# Tworzymy warstwę, która będzie zawierać wszystkie nawierzchnie z jednolitym kolorem
all_surfaces_layer = folium.FeatureGroup(name="Wszystkie nawierzchnie", show=False)

for surface_type in unique_surface_types:
    surface_layer = folium.FeatureGroup(name=f"Nawierzchnia: {surface_type}", show=False)
    
    # Tworzymy warstwę tylko dla geometrii typu LineString
    for _, row in data2.iterrows():
        if row.geometry.geom_type == 'LineString' and row["MATE_NAWIE"] == surface_type:
            folium.PolyLine(
                locations=[(point[1], point[0]) for point in row.geometry.coords],
                color=surface_colors.get(surface_type, 'gray'),  # Kolor z mapy, domyślnie szary
                weight=3, opacity=1
            ).add_to(surface_layer)
            
            # Dodajemy każdą nawierzchnię również do warstwy "Wszystkie nawierzchnie"
            folium.PolyLine(
                locations=[(point[1], point[0]) for point in row.geometry.coords],
                color='black',  # Jednolity kolor dla wszystkich nawierzchni
                weight=2, opacity=1
            ).add_to(all_surfaces_layer)
    
    surface_layers[surface_type] = surface_layer
    surface_layer.add_to(m)

# Dodanie warstw do mapy
marker_layer.add_to(m)
all_surfaces_layer.add_to(m)

# Dodanie przełącznika warstw
folium.LayerControl().add_to(m)

# Zapisanie mapy do pliku HTML
m.save("heatmap_warszawa.html")
m
