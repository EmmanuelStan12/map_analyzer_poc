import os

from app.src.data.polygon_referenced_by_country import PolygonReferencedByCountry
from app.src.data.polygon_referenced_by_state import PolygonReferencedByState
from app.src.grid import create_grid, clip_grid
from app.src.polygon import extract_polygons
from app.src.reader import read_geojson


def extract_states(geo_df, states):
    """
    Extract specific states from a GeoDataFrame.

    Args:
        geo_df (GeoDataFrame): The input GeoDataFrame.
        states (list): A list of state names to extract.

    Returns:
        GeoDataFrame: A GeoDataFrame containing only the specified states.
    """
    return geo_df[geo_df['state'].isin(states)]


def extract_and_save_geojson_file_as_polygons(conn, referenced_by_country=False):
    """
   Extracts polygons from a GeoJSON file, creates a grid, clips the grid with the input map,
   and saves the polygons to the database.

   Args:
       conn (Connection Engine): Database connection engine.
       referenced_by_country (bool): Save geojson as referenced by country or state.
   """
    geojson_path = os.getenv("GEOJSON_INPUT_PATH")

    if not geojson_path:
        raise ValueError("Environment variable GEOJSON_INPUT_PATH not set")

    # Declare width and height of each square in the grid in degrees
    grid_size_km = 33  # 33 km
    width, height = kilometres_to_degrees(grid_size_km)

    # Read the geojson file
    input_map_gdf = read_geojson(geojson_path, referenced_by_country)
    grid = create_grid(input_map_gdf, height, width)

    # Clipped map
    clipped_map_gdf = clip_grid(grid, input_map_gdf)

    polygons = extract_polygons(clipped_map_gdf, height, width, referenced_by_country)

    if referenced_by_country:
        insert = PolygonReferencedByCountry.batch_insert_geopolygon
    else:
        insert = PolygonReferencedByState.batch_insert_geopolygon
    insert(conn, polygons)


def kilometres_to_degrees(kilometres):
    """
    Converts a distance in kilometres to degrees.

    Args:
        kilometres (float): Distance in kilometres.

    Returns:
        float: Distance in degrees.
    """
    # The value of 1 deg latitude at the poles is 111.699km and at the equator is 110.567km
    # but for latitude we use an approximate acceptable value which is 1 deg = 110.574km
    # however since the focus case is in nigeria, we can get the upper bounds and lower bounds of nigeria and
    # compute the average to get a better approximation of each width for a grid.
    height = kilometres / 110.574

    # The value of longitude varies largely due to the distance between each line varies from the poles to the equator.
    # for longitude, deg = cos(latitude) * length of degrees at the equator (111.32km)
    # But for more accurate readings we can calculate this to get an average value of 109.85612km/deg
    # This can be done using the Circumference of the circle at the middle of nigeria divided by 360 deg.
    # From calculation this C(Nigeria) = 39,548.204929km
    width = kilometres / 109.85612
    return width, height
