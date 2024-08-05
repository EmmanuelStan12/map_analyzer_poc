import os

from dotenv import load_dotenv

from app.src.map.data.db import init_conn
from app.src.map.data.polygon_referenced_by_country import PolygonReferencedByCountry
from app.src.map.data.state import State
from app.src.map.utils.export import export_geo_dataframe

load_dotenv()

if __name__ == "__main__":
    # The output path could be html, geojson or kml
    output_path = os.getenv("OUTPUT_PATH")
    conn = init_conn()
    State.get_all_states(conn)
    country_polygon = PolygonReferencedByCountry.find_polygon_by_point(conn, 7.4667522, 9.0695949)
    export_geo_dataframe([country_polygon], referenced_by_country=True, file_path=output_path)
