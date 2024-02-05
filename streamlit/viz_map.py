import streamlit as st
import geopandas as gpd
import folium
import random
from streamlit_folium import folium_static
import psycopg2
import json
import pyproj

def data_from_database():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="geojson",
            user="postgres",
            password="kyuura20020929"
        )
    except psycopg2.Error as e:
        st.error(f"Error connecting to the database: {e}")
        return
    
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM desa_kel_yd")
        rows = cur.fetchall()
    except psycopg2.Error as e:
        st.error(f"Error executing query: {e}")
        return
    finally:
        cur.close()
        conn.close()

    # Membuat struktur data GeoJSON
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    # Iterasi melalui setiap baris data
    for row in rows:
        # Mengambil kolom yang sesuai
        object_id, namobj, kdcpum, wadmkc, wadmkd, wadmkk, wadmpr, luas, json_data = row
        value = json_data

        # Membuat fitur GeoJSON
        feature = {
            "type": "Feature",
            "properties": {
                "OBJECTID": object_id,
                "NAMOBJ": namobj,
                "KDCPUM": kdcpum,
                "WADMKC": wadmkc,
                "WADMKD": wadmkd,
                "WADMKK": wadmkk,
                "WADMPR": wadmpr,
                "luas": luas
            },
            "geometry": value['geometry']
        }
        # Menambahkan fitur ke koleksi GeoJSON
        geojson["features"].append(feature)
    return geojson

def generate_random_color():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    hex_color = "#{:02X}{:02X}{:02X}".format(red, green, blue)
    return hex_color

def visualize_geojson(show_color=True, show_marker=True):

    # Ambil data daridatabase
    geojson_data = data_from_database()
    
    # Konversi GeoJSON menjadi GeoDataFrame
    data = gpd.GeoDataFrame.from_features(geojson_data["features"])
    data.crs = pyproj.CRS.from_epsg(4326).to_wkt()

    selected_wadmkc = st.sidebar.selectbox('Pilih Kode Wilayah Administrasi:', data['WADMKC'].unique())
    filtered_data = data[data['WADMKC'] == selected_wadmkc]

    # Mengonversi seluruh GeoDataFrame ke EPSG:4326
    filtered_data = filtered_data.to_crs("EPSG:4326")

    # Menghitung centroid dalam EPSG:4326
    centroid_y = filtered_data.geometry.centroid.y.mean()
    centroid_x = filtered_data.geometry.centroid.x.mean()

    m = folium.Map(location=[centroid_y, centroid_x], zoom_start=13)

    show_color_checkbox = st.sidebar.checkbox("Tampilkan Warna", value=show_color)

    fill_opacity = 0.3
    line_opacity = 0.8

    unique_colors = {name: generate_random_color() if show_color_checkbox else "#7EB3FF" for name in filtered_data['NAMOBJ'].unique()}

    # Show Color Checkbox
    geojson_layer = folium.GeoJson(filtered_data,
                                style_function=lambda feature: {
                                    'fillColor': unique_colors.get(feature['properties']['NAMOBJ'], 'gray'),
                                    'fillOpacity': fill_opacity,
                                    'color': 'black',
                                    'weight': 1,
                                    'opacity': line_opacity
                                })
    geojson_layer.add_to(m)

    # Show Marker Checkbox
    show_marker_checkbox = st.sidebar.checkbox("Tampilkan Marker", value=show_marker)

    if show_marker_checkbox:
        for idx, row in filtered_data.iterrows():
            if row['geometry'].geom_type == 'Polygon':
                coordinates = row['geometry'].exterior.coords.xy
            else:  # MultiPolygon
                coordinates = row['geometry'].centroid.coords.xy

            link_web = f"http://{str(row['NAMOBJ']).lower()}-{selected_wadmkc.lower()}.desa.id"
            folium.Marker([coordinates[1][0], coordinates[0][0]],
                        popup=f"<b>{row['NAMOBJ']}</b><br>{row['WADMKC']}<br><a href='{link_web}' target='_blank'>{link_web}</a>").add_to(m)

    folium_static(m)

# Main Streamlit App
show_color = True
show_marker = True


st.set_page_config(
    page_title="Peta Wilayah Kabupaten Sidorjo",
    page_icon="icon/LogoSidoarjo-modified.ico", 
)

st.title('Peta Wilayah Kabupaten Sidoarjo')

st.sidebar.title("Wilayah")

# Memanggil fungsi visualisasi saat aplikasi Streamlit dijalankan
visualize_geojson(show_color, show_marker)