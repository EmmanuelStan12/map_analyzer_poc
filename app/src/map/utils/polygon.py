from app.src.map.data.polygon_referenced_by_country import PolygonReferencedByCountry
from app.src.map.data.polygon_referenced_by_state import PolygonReferencedByState
from app.src.map.data.state import State


def create_state_polygon(geom, grid_height, grid_width, i, max_x, max_y, min_x, min_y, props):
    """
    Create a PolygonReferencedByState object from geometry and metadata.

    Args:
        geom (Geometry): The geometry of the polygon.
        grid_height (float): The height of each grid cell.
        grid_width (float): The width of each grid cell.
        i (int): The index of the current geometry.
        max_x (float): The maximum x-coordinate of the grid bounds.
        max_y (float): The maximum y-coordinate of the grid bounds.
        min_x (float): The minimum x-coordinate of the grid bounds.
        min_y (float): The minimum y-coordinate of the grid bounds.
        props (dict): The properties of the geometry.

    Returns:
        PolygonReferencedByState: The created GeoPolygon object.
    """
    # Calculate the row and column index for the current geometry
    row_index = i // int((max_y - min_y) / grid_height)
    col_index = i % int((max_x - min_x) / grid_width)

    # Prepare metadata for the polygon
    metadata = {
        'left': geom.bounds[0],
        'top': geom.bounds[3],
        'right': geom.bounds[2],
        'bottom': geom.bounds[1],
        'index': i,
        'row_index': row_index,
        'col_index': col_index,
    }

    # Extract coordinates from the geometry
    coords = list(geom.exterior.coords)

    props_getter = lambda key: props[key] if key in props else ''

    # Retrieve the state object by its code, this only applies for geojson with statecode as a prop parameter.
    code = props_getter('statecode')
    states = State.get_states_by_code()
    state = None
    if code in states:
        state = states[code]
    else:
        print(f"Cannot find state with code: {code}")

    # Create and return the PolygonReferencedByState object
    return PolygonReferencedByState(
        object_id=props_getter('objectid'),
        state=state,
        cap_city=props_getter('capcity'),
        source=props_getter('source'),
        shape_area=props_getter('shape_area'),
        shape_length=props_getter('shape_len'),
        geo_zone=props_getter('geozone'),
        coordinates=coords,
        metadata=metadata,
    )


def create_country_polygon(geom, grid_height, grid_width, i, max_x, max_y, min_x, min_y, props):
    """
    Create a PolygonReferencedByCountry object from geometry and metadata.

    Args:
        geom (Geometry): The geometry of the polygon.
        grid_height (float): The height of each grid cell.
        grid_width (float): The width of each grid cell.
        i (int): The index of the current geometry.
        max_x (float): The maximum x-coordinate of the grid bounds.
        max_y (float): The maximum y-coordinate of the grid bounds.
        min_x (float): The minimum x-coordinate of the grid bounds.
        min_y (float): The minimum y-coordinate of the grid bounds.
        props (dict): The properties of the geometry.

    Returns:
        PolygonReferencedByCountry: The created GeoPolygon object.
    """
    # Extract coordinates from the geometry
    coords = list(geom.exterior.coords)
    props_getter = lambda key: props[key] if key in props else ''

    # Create and return the PolygonReferencedByCountry object
    return PolygonReferencedByCountry(
        shape_area=props_getter('shape_area'),
        shape_length=props_getter('shape_len'),
        coordinates=coords
    )


def extract_polygons(geo_df, grid_height, grid_width, referenced_by_country=False):
    """
    Extract all polygons from a GeoDataFrame.

    Args:
        geo_df (GeoDataFrame): The GeoDataFrame to extract from.
        grid_height (float): The height of each grid cell.
        grid_width (float): The width of each grid cell.
        referenced_by_country (bool): Flag to determine whether to reference by state or country.

    Returns:
        list: A list of GeoPolygon objects.
    """
    # Get the bounds of the GeoDataFrame
    min_x, min_y, max_x, max_y = geo_df.total_bounds
    polygons = []

    # Determine which create_polygon function to use
    if referenced_by_country:
        create_polygon = create_country_polygon
    else:
        create_polygon = create_state_polygon

    # Iterate over each row in the GeoDataFrame
    for i, row in geo_df.iterrows():
        geom = row.geometry
        props = row.drop('geometry')

        # Handle single Polygon geometries
        if geom.geom_type == 'Polygon':
            polygon = create_polygon(geom, grid_height, grid_width, i, max_x, max_y, min_x, min_y, props)
            polygons.append(polygon)

        # Handle MultiPolygon geometries by iterating over each polygon
        elif geom.geom_type == 'MultiPolygon':
            for polygon in geom.geoms:
                polygon = create_polygon(polygon, grid_height, grid_width, i, max_x, max_y, min_x, min_y, props)
                polygons.append(polygon)

    return polygons
