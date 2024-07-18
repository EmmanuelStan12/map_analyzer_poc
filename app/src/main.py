import os

from app.src.map import *
import mysql.connector
from dotenv import load_dotenv


load_dotenv()

if __name__ == "__main__":
    # The output path could be html, geojson or kml
    output_path = os.getenv("OUTPUT_PATH")
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    # extract_and_save_geojson_file(conn)
    state_polygons = GeoPolygon.find_polygons_by_state(conn, ['Ogun', 'Kaduna'])
    state_map = build_geojson_from_polygons(state_polygons)
    plot_geojson(state_map, output_path)
