import psycopg2
import json

with open ('data/Des_Kel_YD.geojson') as file:
    geojson_data = json.load(file)

conn = psycopg2.connect(
    host="localhost",
    database="geojson",
    user="postgres",
    password="kyuura20020929",
    port="5432"
)

cur = conn.cursor()

cur.execute("""
    CREATE TABLE desa_kel_yd (
        objectid VARCHAR PRIMARY KEY,
        namobj VARCHAR,
        kdcpum VARCHAR,
        wadmkc VARCHAR,
        wadmkd VARCHAR,
        wadmkk VARCHAR,
        wadmpr VARCHAR,
        luas NUMERIC,
        coordinates JSONB
    )
""")
conn.commit()

for feature in geojson_data['features']:
    objectid = feature['properties']['OBJECTID']
    namobj = feature['properties']['NAMOBJ']
    kdcpum = feature['properties']['KDCPUM']
    wadmkc = feature['properties']['WADMKC']
    wadmkd = feature['properties']['WADMKD']
    wadmkk = feature['properties']['WADMKK']
    wadmpr = feature['properties']['WADMPR']
    luas = feature['properties']['luas']
    coordinates = feature['geometry']['coordinates']
    
    template = {
        'type' : 'Polygon',
        'geometry' : {
            'type' : 'Polygon',
            'coordinates' : coordinates
        }
    }

    cur.execute("""
        INSERT INTO desa_kel_yd (objectid, namobj, kdcpum, wadmkc, wadmkd, wadmkk, wadmpr, luas, coordinates)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (objectid, namobj, kdcpum, wadmkc, wadmkd, wadmkk, wadmpr, luas, json.dumps(template)))
    
conn.commit()

cur.close()

conn.close()