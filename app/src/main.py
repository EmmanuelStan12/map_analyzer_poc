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
    # state_polygons = GeoPolygon.find_polygons_by_state(conn, ['Ogun', 'Kaduna'])
    # state_polygon = GeoPolygon.find_polygon_by_point(conn, 7.597030332256636, 9.355428925147828)
    polygons = GeoPolygon.get_all_polygons(conn)
    state_map = build_geo_dataframe_from_polygons(polygons)
    plot_geo_dataframe(state_map, output_path)
