import os

from app.src.data.polygon_referenced_by_country import PolygonReferencedByCountry
from app.src.data.polygon_referenced_by_state import PolygonReferencedByState
from app.src.data.state import State
import mysql.connector
from dotenv import load_dotenv

from app.src.extract import extract_and_save_geojson_file_as_polygons
from app.src.plot import build_geo_dataframe_from_polygons, plot_geo_dataframe

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
    State.get_all_states(conn)
    # extract_and_save_geojson_file_as_polygons(conn, False)
    state_polygons = PolygonReferencedByState.find_polygons_by_state(conn, ['Ogun', 'Kaduna', 'Sokoto'])
    # state_polygon = PolygonReferencedByState.find_polygon_by_point(conn, 7.332974557356726, 8.569431552668998)
    # country_polygon = PolygonReferencedByCountry.find_polygon_by_point(conn, 4.650460555129401, 13.582704599916504)
    # polygons = PolygonReferencedByCountry.get_all_polygons(conn)
    state_map = build_geo_dataframe_from_polygons(state_polygons)
    # country_map = build_geo_dataframe_from_polygons(polygons, True)
    # Define styles
    style1 = {'fillColor': '#333366', 'color': '#134B70', 'fillOpacity': 0.2, 'weight': 1}
    # style2 = {'fillColor': '#EB4D55', 'color': '#EB4D55', 'fillOpacity': 0.2, 'weight': 1}
    #
    plot_geo_dataframe([(state_map, "Layer 1", style1)], output_path)
