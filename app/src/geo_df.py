import geopandas as gpd
from shapely import Polygon


def build_geo_dataframe_from_polygons(polygons, referenced_by_country=False):
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
        referenced_by_country (bool): This determines to build the frame as a country or state.

    Returns:
        GeoDataFrame: A GeoDataFrame representing the input polygons.
    """
    if referenced_by_country:
        return build_geo_dataframe_from_polygons_by_country(polygons)
    return build_geo_dataframe_from_polygons_by_state(polygons)


def build_geo_dataframe_from_polygons_by_state(polygons):
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
        'state_code': [(polygon.state.code if polygon.state is not None else '') for polygon in polygons],
        'state': [(polygon.state.name if polygon.state is not None else '') for polygon in polygons],
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


def build_geo_dataframe_from_polygons_by_country(polygons):
    polygons_data = {
        'shape_area': [polygon.shape_area for polygon in polygons],
        'shape_length': [polygon.shape_length for polygon in polygons],
        'geometry': [Polygon(polygon.coordinates) for polygon in polygons],
        'object_id': [polygon.pid for polygon in polygons]
    }

    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(polygons_data, crs='EPSG:4326')

    # Optional: Set index if needed
    gdf.set_index('object_id', inplace=True)

    return gdf
