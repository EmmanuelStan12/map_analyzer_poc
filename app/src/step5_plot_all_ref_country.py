import os

from dotenv import load_dotenv

from app.src.data.db import init_conn
from app.src.data.polygon_referenced_by_country import PolygonReferencedByCountry
from app.src.data.state import State
from app.src.export import export_geo_dataframe

load_dotenv()

if __name__ == "__main__":
    # The output path could be html, geojson or kml
    output_path = os.getenv("OUTPUT_PATH")
    conn = init_conn()
    State.get_all_states(conn)
    polygons = PolygonReferencedByCountry.get_all_polygons(conn)
    export_geo_dataframe(polygons, referenced_by_country=True, file_path=output_path)
