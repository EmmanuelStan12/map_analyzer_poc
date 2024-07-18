import os

import geopandas as gpd
from lxml import etree
from shapely import Polygon
from shapely.geometry import box
from pykml.factory import KML_ElementMaker
import folium
import pandas as pd
from app.src.data.geo_polygon import GeoPolygon


def read_geojson(path):
    """
    Reads a GeoJSON file and converts it to a GeoDataFrame.

    Args:
        path (str): The absolute path of the GeoJSON file.

    Returns:
        GeoDataFrame: A GeoDataFrame created from the file.
    """
    return gpd.read_file(path)


def create_grid(geo_df, grid_height, grid_width):
    """
    Create a rectangular grid over the bounding box of a GeoDataFrame.

    Args:
        geo_df (GeoDataFrame): The input GeoDataFrame.
        grid_height (float): The height of each grid cell.
        grid_width (float): The width of each grid cell.

    Returns:
        GeoDataFrame: A GeoDataFrame containing the grid cells as geometries.
    """
    min_x, min_y, max_x, max_y = geo_df.total_bounds
    grid_cells = []

    x = min_x
    while x < max_x:
        y = min_y
        while y < max_y:
            grid_cells.append(box(x, y, x + grid_width, y + grid_height))
            y += grid_height
        x += grid_width

    return gpd.GeoDataFrame({'geometry': grid_cells}, crs=geo_df.crs)


def clip_grid(grid_geo_df, map_geo_df):
    """
    Clip the grid cells with the given map to keep only the intersecting areas.

    Args:
        grid_geo_df (GeoDataFrame): The grid GeoDataFrame.
        map_geo_df (GeoDataFrame): The map GeoDataFrame to clip against.

    Returns:
        GeoDataFrame: A GeoDataFrame with the clipped grid cells.
    """
    return gpd.overlay(grid_geo_df, map_geo_df, how='intersection')


def export_to_geojson(geo_df, file_path):
    """
    Export the given GeoDataFrame to a GeoJSON file.

    Args:
        geo_df (GeoDataFrame): The GeoDataFrame to export.
        file_path (str): The file path to save the GeoJSON.
    """
    geo_df.to_file(file_path, driver="GeoJSON")


def create_polygon(geom, grid_height, grid_width, i, max_x, max_y, min_x, min_y, props):
    """
    Create a GeoPolygon object from geometry and metadata.

    Args:
        geom (Geometry): The geometry of the polygon.
        grid_height (float): The height of each grid cell.
        grid_width (float): The width of each grid cell.
        i (int): The index of the current geometry.
        max_x, max_y, min_x, min_y (float): The bounds of the grid.
        props (dict): The properties of the geometry.

    Returns:
        GeoPolygon: The created GeoPolygon object.
    """
    row_index = i // int((max_y - min_y) / grid_height)
    col_index = i % int((max_x - min_x) / grid_width)
    metadata = {
        'left': geom.bounds[0],
        'top': geom.bounds[3],
        'right': geom.bounds[2],
        'bottom': geom.bounds[1],
        'index': i,
        'row_index': row_index,
        'col_index': col_index,
    }

    coords = list(geom.exterior.coords)

    return GeoPolygon(
        object_id=props['objectid'],
        state_code=props['statecode'],
        state=props['state'],
        cap_city=props['capcity'],
        source=props['source'],
        shape_area=props['shape_area'],
        shape_length=props['shape_len'],
        geo_zone=props['geozone'],
        timestamp=props['timestamp'],
        created_at=props['created_at'],
        updated_at=props['updated_at'],
        coordinates=coords,
        metadata=metadata,
    )


def extract_polygons(geo_df, grid_height, grid_width):
    """
    Extract all polygons from a GeoDataFrame.

    Args:
        geo_df (GeoDataFrame): The GeoDataFrame to extract from.
        grid_height (float): The height of each grid cell.
        grid_width (float): The width of each grid cell.

    Returns:
        list: A list of GeoPolygon objects.
    """
    min_x, min_y, max_x, max_y = geo_df.total_bounds
    polygons = []

    for i, row in geo_df.iterrows():
        geom = row.geometry
        props = row.drop('geometry')

        if geom.geom_type == 'Polygon':
            polygon = create_polygon(geom, grid_height, grid_width, i, max_x, max_y, min_x, min_y, props)
            polygons.append(polygon)

        elif geom.geom_type == 'MultiPolygon':
            for polygon in geom.geoms:
                polygon = create_polygon(polygon, grid_height, grid_width, i, max_x, max_y, min_x, min_y, props)
                polygons.append(polygon)

    return polygons


def create_kml_placemark(polygon, grid_height, grid_width):
    """
    Create a KML placemark from a GeoPolygon object.

    Args:
        polygon (GeoPolygon): The GeoPolygon object.
        grid_height (float): The height of each grid cell.
        grid_width (float): The width of each grid cell.

    Returns:
        KML Element: The created KML placemark element.
    """
    coords = list(polygon.coordinates)
    coord_str = " ".join(f"{coord[0]},{coord[1]}" for coord in coords)

    return KML_ElementMaker.Placemark(
        KML_ElementMaker.Style(
            KML_ElementMaker.LineStyle(KML_ElementMaker.color("ff0000ff")),
            KML_ElementMaker.PolyStyle(KML_ElementMaker.fill(0))
        ),
        KML_ElementMaker.ExtendedData(
            KML_ElementMaker.SchemaData(
                KML_ElementMaker.SimpleData(f"{polygon.metadata['index']}", name="id"),
                KML_ElementMaker.SimpleData(f"{polygon.metadata['left']}", name="left"),
                KML_ElementMaker.SimpleData(f"{polygon.metadata['top']}", name="top"),
                KML_ElementMaker.SimpleData(f"{polygon.metadata['right']}", name="right"),
                KML_ElementMaker.SimpleData(f"{polygon.metadata['bottom']}", name="bottom"),
                KML_ElementMaker.SimpleData(f"{polygon.metadata['row_index']}", name="row_index"),
                KML_ElementMaker.SimpleData(f"{polygon.metadata['col_index']}", name="col_index"),
                schemaUrl="#clipped"
            )
        ),
        KML_ElementMaker.MultiGeometry(
            KML_ElementMaker.Polygon(
                KML_ElementMaker.outerBoundaryIs(
                    KML_ElementMaker.LinearRing(
                        KML_ElementMaker.coordinates(coord_str)
                    )
                )
            )
        )
    )


def export_to_kml(polygons, file_path, grid_height, grid_width):
    """
    Export the given GeoDataFrame to a KML file.

    Args:
        polygons (list): The list of polygons to export.
        file_path (str): The file path to save the KML.
        grid_height (float): The height of each grid cell.
        grid_width (float): The width of each grid cell.
    """
    place_marks = []

    for polygon in polygons:
        place_mark = create_kml_placemark(polygon, grid_height, grid_width)
        place_marks.append(place_mark)

    kml_document = KML_ElementMaker.kml(KML_ElementMaker.Document(*place_marks))

    with open(file_path, 'w') as file:
        file.write(etree.tostring(kml_document, pretty_print=True).decode('utf-8'))


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


def plot_geo_dataframe(geo_df, output_file):
    """
    Plot a GeoDataFrame on a Folium map and save it as an HTML file.

    Args:
        geo_df (GeoDataFrame): The input GeoDataFrame.
        output_file (str): The file path to save the HTML map.
    """
    geo_df = geo_df.copy()

    # Convert datetime columns to strings
    for column in geo_df.columns:
        if pd.api.types.is_datetime64_any_dtype(geo_df[column].dtype):
            geo_df[column] = geo_df[column].astype(str)

    # Re-project the GeoDataFrame to Web Mercator CRS
    geo_df = geo_df.to_crs(epsg=3857)

    # Get the centroid of the GeoDataFrame for the initial map center
    centroid = geo_df.geometry.centroid.to_crs(epsg=4326)
    map_center = [centroid.y.mean(), centroid.x.mean()]

    # Create a folium map centered at the centroid of the GeoJSON data
    folium_map = folium.Map(location=map_center, zoom_start=6)

    # Add the GeoJSON layer to the map
    folium.GeoJson(geo_df, name='geojson').add_to(folium_map)

    # Add layer control to toggle the GeoJSON layer
    folium.LayerControl().add_to(folium_map)

    # Save the map as an HTML file
    folium_map.save(output_file)


def build_geo_dataframe_from_polygons(polygons):
    """
    Build a GeoDataFrame from a list of polygon objects and return it.

    Args:
        polygons (list): List of polygon objects. Each polygon object must have the following attributes:
                         - object_id
                         - state_code
                         - state
                         - cap_city
                         - source
                         - shape_area
                         - shape_length
                         - geo_zone
                         - coordinates (list of tuples representing the polygon's vertices)

    Returns:
        GeoDataFrame: A GeoDataFrame representing the input polygons.
    """
    polygons_data = {
        'object_id': [polygon.object_id for polygon in polygons],
        'state_code': [polygon.state_code for polygon in polygons],
        'state': [polygon.state for polygon in polygons],
        'cap_city': [polygon.cap_city for polygon in polygons],
        'source': [polygon.source for polygon in polygons],
        'shape_area': [polygon.shape_area for polygon in polygons],
        'shape_length': [polygon.shape_length for polygon in polygons],
        'geo_zone': [polygon.geo_zone for polygon in polygons],
        'geometry': [Polygon(polygon.coordinates) for polygon in polygons]
    }

    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(polygons_data, crs='EPSG:4326')

    # Optional: Set index if needed
    gdf.set_index('object_id', inplace=True)

    return gdf


def extract_and_save_geojson_file_as_polygons(conn):
    """
   Extracts polygons from a GeoJSON file, creates a grid, clips the grid with the input map,
   and saves the polygons to the database.

   Args:
       conn (Connection Engine): Database connection engine.
   """
    geojson_path = os.getenv("GEOJSON_INPUT_PATH")

    if not geojson_path:
        raise ValueError("Environment variable GEOJSON_INPUT_PATH not set")

    # Declare width and height of each square in the grid in degrees
    grid_size_km = 33  # 33 km
    width, height = kilometres_to_degrees(grid_size_km)

    # Read the geojson file
    input_map_gdf = read_geojson(geojson_path)
    grid = create_grid(input_map_gdf, height, width)

    # Clipped map
    clipped_map_gdf = clip_grid(grid, input_map_gdf)

    polygons = extract_polygons(clipped_map_gdf, height, width)

    GeoPolygon.batch_insert_geopolygon(conn, polygons)


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
