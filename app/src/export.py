from lxml import etree
from pykml.factory import KML_ElementMaker


def export_to_geojson(geo_df, file_path):
    """
    Export the given GeoDataFrame to a GeoJSON file.

    Args:
        geo_df (GeoDataFrame): The GeoDataFrame to export.
        file_path (str): The file path to save the GeoJSON.
    """
    geo_df.to_file(file_path, driver="GeoJSON")


def create_kml_placemark(polygon, grid_height, grid_width):
    """
    Create a KML placemark from a GeoPolygon object.

    Args:
        polygon (PolygonReferencedByState): The GeoPolygon object.
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
