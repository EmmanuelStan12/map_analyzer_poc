from dotenv import load_dotenv
from flask import Flask, request, jsonify

from app.src.map.data.db import init_conn
from app.src.map.data.polygon_referenced_by_country import PolygonReferencedByCountry
from app.src.map.data.polygon_referenced_by_state import PolygonReferencedByState
from app.src.map.data.state import State
from app.src.map.utils.export import export_geo_dataframe, ExportType
from app.src.map.utils.extract import extract_and_save_geojson_file_as_polygons

app = Flask(__name__)

load_dotenv()

conn = init_conn()
State.get_all_states(conn)


@app.route('/')
def hello():
    return success_response(200, 'Hello, World!')


@app.route('/extract-polygons', methods=['POST'])
def extract_polygons():
    try:
        body = request.get_json()
        reference = body.get('reference')
        width = body.get('width')
        height = body.get('height')
        extract_and_save_geojson_file_as_polygons(conn, grid_width=width, grid_height=height, referenced_by_country=(reference == "COUNTRY"))
        return success_response(201, 'Data extracted successfully')
    except Exception as e:
        return error_response(500, str(e))


@app.route('/plot/<string:reference>/<float:latitude>/<float:longitude>/<string:export_type>', methods=['GET'])
def plot_polygons_by_point(reference, latitude, longitude, export_type):
    try:
        if reference == "STATE":
            polygon = PolygonReferencedByState.find_polygon_by_point(conn, longitude, latitude)
        else:
            polygon = PolygonReferencedByCountry.find_polygon_by_point(conn, longitude, latitude)

        result = export_geo_dataframe([polygon], export_type=ExportType.value_of(export_type),
                                      referenced_by_country=(reference == "COUNTRY"))

        return result
    except ValueError as e:
        return error_response(400, str(e))
    except Exception as e:
        return error_response(500, str(e))


@app.route('/plot/<string:export_type>', methods=['GET'])
def plot_state_polygons(export_type):
    try:
        state_codes = request.args.get('state_codes').split(",")
        print(state_codes)
        polygons = PolygonReferencedByState.find_polygons_by_state(conn, state_codes)
        result = export_geo_dataframe(polygons, export_type=ExportType.value_of(export_type),
                                      referenced_by_country=False)

        return result
    except Exception as e:
        return error_response(500, str(e))


def success_response(code, data):
    return jsonify({
        'code': code,
        'data': data
    })


def error_response(code, message):
    return jsonify({
        'code': code,
        'message': message
    })


if __name__ == "__main__":
    app.run(debug=True)
