import geopandas as gpd
from shapely import box


def clip_grid(grid_geo_df, map_geo_df):
    """
    Clip the grid cells with the given map to keep only the intersecting areas.

    Args:
        grid_geo_df (GeoDataFrame): The grid GeoDataFrame.
        map_geo_df (GeoDataFrame): The map GeoDataFrame to clip against.

    Returns:
        GeoDataFrame: A GeoDataFrame with the clipped grid cells.
    """
    geo_df = gpd.overlay(grid_geo_df, map_geo_df, how='intersection')

    return geo_df


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
