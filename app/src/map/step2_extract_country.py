from dotenv import load_dotenv

from app.src.map.data.db import init_conn
from app.src.map.data.state import State
from app.src.map.utils.extract import extract_and_save_geojson_file_as_polygons

load_dotenv()

if __name__ == "__main__":
    conn = init_conn()
    State.get_all_states(conn)
    extract_and_save_geojson_file_as_polygons(conn, True)
