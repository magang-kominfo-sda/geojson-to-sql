import json
import psycopg2

# Koneksi ke database
conn = psycopg2.connect(
    host="localhost",
    database="geojson",
    user="postgres",
    password="kyuura20020929"
)

# Membaca data dari tabel desa_kel_yd
cur = conn.cursor()
cur.execute("SELECT * FROM desa_kel_yd")
rows = cur.fetchall()

# Membuat struktur data GeoJSON
geojson = {
    "type": "FeatureCollection",
    "features": []
}

# Iterasi melalui setiap baris data
for row in rows:
    # Mengambil kolom yang sesuai
    object_id = row[0]
    namobj = row[1]
    kdcpum = row[2]
    wadmkc = row[3]
    wadmkd = row[4]
    wadmkk = row[5]
    wadmpr = row[6]
    luas = str(row[7])
    json_data = row[8]
    value = json_data['geometry']

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
            "luas": luas,
        },
        "geometry": value
    }

    # Menambahkan fitur ke koleksi GeoJSON
    geojson["features"].append(feature)

# Menutup koneksi ke database
conn.close()

# Menyimpan struktur data GeoJSON ke file
with open('output2.geojson', 'w') as file:
    json.dump(geojson, file, indent= 2)