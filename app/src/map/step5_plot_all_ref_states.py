import os

from dotenv import load_dotenv

from app.src.map.data.db import init_conn
from app.src.map.data.polygon_referenced_by_state import PolygonReferencedByState
from app.src.map.data.state import State
from app.src.map.utils.export import export_geo_dataframe

load_dotenv()

if __name__ == "__main__":
    # The output path could be html, geojson or kml
    output_path = os.getenv("OUTPUT_PATH")

    conn = init_conn()
    State.get_all_states(conn)
    polygons = PolygonReferencedByState.get_all_polygons(conn)
    export_geo_dataframe(polygons, referenced_by_country=False, file_path=output_path)

