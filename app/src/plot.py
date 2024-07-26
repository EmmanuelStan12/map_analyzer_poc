import folium
import pandas as pd
from shapely import Polygon
import geopandas as gpd


def plot_geo_dataframe(geo_dfs, output_file):
    """
    Plot multiple GeoDataFrames on a Folium map and save it as an HTML file.

    Args:
        geo_dfs (list of tuples): A list of tuples where each tuple contains a GeoDataFrame, a layer name, and a style dictionary.
        output_file (str): The file path to save the HTML map.
    """
    # Create an empty map with a reasonable default location
    folium_map = folium.Map(location=[0, 0], zoom_start=2)

    for geo_df, layer_name, style in geo_dfs:
        geo_df = geo_df.copy()

        # Convert datetime columns to strings
        for column in geo_df.columns:
            if pd.api.types.is_datetime64_any_dtype(geo_df[column].dtype):
                geo_df[column] = geo_df[column].astype(str)

        # Re-project the GeoDataFrame to Web Mercator CRS which is used by maps visualization tools
        geo_df = geo_df.to_crs(epsg=3857)

        # Get the centroid of the GeoDataFrame for the initial map center
        centroid = geo_df.geometry.centroid.to_crs(epsg=4326)
        map_center = [centroid.y.mean(), centroid.x.mean()]

        # Update the map center to be the centroid of the first GeoDataFrame
        if folium_map.location == [0, 0]:
            folium_map.location = map_center
            folium_map.zoom_start = 6

        # Define a style function for the GeoJSON layer
        s_func = lambda x: style

        # Add the GeoJSON layer to the map
        folium.GeoJson(geo_df, name=layer_name, style_function=s_func).add_to(folium_map)

    # Add layer control to toggle the GeoJSON layer
    folium.LayerControl().add_to(folium_map)

    # Save the map as an HTML file
    folium_map.save(output_file)


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
        'state_code': [polygon.state.code for polygon in polygons],
        'state': [polygon.state.name for polygon in polygons],
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
