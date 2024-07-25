import geopandas as gpd
from shapely.validation import explain_validity


def read_geojson(path, reference_by_country=False):
    """
    Reads a GeoJSON file and converts it to a GeoDataFrame.

    Args:
        path (str): The absolute path of the GeoJSON file.
        reference_by_country (bool): read the geojson as referenced by country to dissolve.

    Returns:
        GeoDataFrame: A GeoDataFrame created from the file.
    """
    # For generating clipped grid with dissolved internal boundaries
    map_geo_df = gpd.read_file(path)
    if reference_by_country:
        map_geo_df = validate_and_clean_geometries(map_geo_df)
        map_geo_df = map_geo_df.dissolve()
    return map_geo_df


def validate_and_clean_geometries(map_df):
    cleaned_geometries = []
    for geom in map_df['geometry']:
        cleaned_geom = validate_and_clean_geometry(geom)
        cleaned_geometries.append(cleaned_geom)

    map_df['geometry'] = cleaned_geometries
    return map_df


def validate_and_clean_geometry(geom):
    if not geom.is_valid:
        print(f"Invalid geometry: {explain_validity(geom)}")
    geom = geom.buffer(0)
    return geom
