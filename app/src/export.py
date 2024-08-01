import folium
from lxml import etree
from pykml.factory import KML_ElementMaker
from enum import Enum, auto
import pandas as pd

from app.src.geo_df import build_geo_dataframe_from_polygons


class ExportType(Enum):
    HTML = auto()
    KML = auto()
    GEO_JSON = auto()


def export_to_geojson(polygons, **opts):
    """
    Export the given GeoDataFrame to a GeoJSON file.

    Args:
        geo_df (GeoDataFrame): The GeoDataFrame to export.
        file_path (str): The file path to save the GeoJSON.
        :param polygons:
    """
    referenced_by_country = opts.get('referenced_by_country')
    file_path = opts.get('file_path')
    geo_df = build_geo_dataframe_from_polygons(polygons,
                                               False if referenced_by_country is None else referenced_by_country)
    geo_df.to_file(file_path, driver="GeoJSON")


def create_kml_placemark(polygon):
    """
    Create a KML placemark from a GeoPolygon object.

    Args:
        polygon (PolygonReferencedByState): The GeoPolygon object.

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


def export_to_kml(polygons, **opts):
    """
    Export the given GeoDataFrame to a KML file.

    Args:
        polygons (list): The list of polygons to export.
    """
    file_path = opts.get('file_path')
    place_marks = []

    for polygon in polygons:
        place_mark = create_kml_placemark(polygon)
        place_marks.append(place_mark)

    kml_document = KML_ElementMaker.kml(KML_ElementMaker.Document(*place_marks))

    with open(file_path, 'w') as file:
        file.write(etree.tostring(kml_document, pretty_print=True).decode('utf-8'))


def export_to_html(polygons, **opts):
    referenced_by_country = opts.get('referenced_by_country')
    file_path = opts.get('file_path')
    geo_df = build_geo_dataframe_from_polygons(polygons,
                                               False if referenced_by_country is None else referenced_by_country)
    style1 = {'fillColor': '#333366', 'color': '#134B70', 'fillOpacity': 0.2, 'weight': 1}

    folium_map = folium.Map(location=[0, 0], zoom_start=2)

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
    s_func = lambda x: style1

    # Add the GeoJSON layer to the map
    folium.GeoJson(geo_df, name="Layer 1", style_function=s_func).add_to(folium_map)

    # Add layer control to toggle the GeoJSON layer
    folium.LayerControl().add_to(folium_map)

    # Save the map as an HTML file
    folium_map.save(file_path)


exports = {
    ExportType.HTML: export_to_html,
    ExportType.KML: export_to_kml,
    ExportType.GEO_JSON: export_to_geojson,
}


def export_geo_dataframe(polygons, export_type=ExportType.HTML, **opts):
    exports[export_type](polygons, **opts)
