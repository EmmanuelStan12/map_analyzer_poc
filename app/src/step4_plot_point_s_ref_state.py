import os

from dotenv import load_dotenv

from app.src.data.db import init_conn
from app.src.data.polygon_referenced_by_state import PolygonReferencedByState
from app.src.data.state import State
from app.src.export import export_geo_dataframe
from app.src.geo_df import build_geo_dataframe_from_polygons

load_dotenv()

if __name__ == "__main__":
    # The output path could be html, geojson or kml
    output_path = os.getenv("OUTPUT_PATH")
    conn = init_conn()
    State.get_all_states(conn)
    state_polygon = PolygonReferencedByState.find_polygon_by_point(conn, 7.4667522, 9.0695949)
    export_geo_dataframe([state_polygon], referenced_by_country=False, file_path=output_path)

