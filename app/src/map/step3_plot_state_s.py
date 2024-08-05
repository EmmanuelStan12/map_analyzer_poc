import os

from dotenv import load_dotenv

from app.src.map.data.db import init_conn
from app.src.map.data.polygon_referenced_by_state import PolygonReferencedByState
from app.src.map.data.state import State
from app.src.map.utils.geo_df import build_geo_dataframe_from_polygons

load_dotenv()

if __name__ == "__main__":
    # The output path could be html, geojson or kml
    output_path = os.getenv("OUTPUT_PATH")
    conn = init_conn()
    State.get_all_states(conn)
    state_polygons = PolygonReferencedByState.find_polygons_by_state(conn, ['FC'])
    state_map = build_geo_dataframe_from_polygons(state_polygons)
    style1 = {'fillColor': '#333366', 'color': '#134B70', 'fillOpacity': 0.2, 'weight': 1}
    build_html_from_geo_dataframes([(state_map, "Layer 1", style1)], output_path)


