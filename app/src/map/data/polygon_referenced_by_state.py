import json
from shapely.geometry import Polygon
import shapely.wkt as wkt

from app.src.map.data.state import State


class PolygonReferencedByState:

    def __init__(self, pid=None, object_id=None, cap_city=None, state=None, source=None,
                 shape_area=None, shape_length=None, geo_zone=None, coordinates=None, metadata=None):
        """
        Initialize a GeoPolygon object.

        Args:
            pid (int): Polygon ID.
            object_id (str): Object ID.
            cap_city (str): Capital city.
            state (State): State.
            source (str): Source of data.
            shape_area (float): Area of the polygon.
            shape_length (float): Perimeter of the polygon.
            geo_zone (str): Geographical zone.
            coordinates (list of tuples): List of (longitude, latitude) coordinates defining the polygon.
            metadata (dict): Additional metadata associated with the polygon.
        """
        self.id = pid
        self.object_id = object_id
        self.state = state
        self.cap_city = cap_city
        self.source = source
        self.shape_area = shape_area
        self.shape_length = shape_length
        self.geo_zone = geo_zone
        self.coordinates = coordinates
        self.metadata = metadata

    @classmethod
    def from_db_row(cls, row):
        """
        Create a GeoPolygon object from a database row.

        Args:
            row (dict): Database row containing polygon data.

        Returns:
            PolygonReferencedByState: Initialized GeoPolygon object.
        """
        metadata = json.loads(row['Metadata'])
        polygon = wkt.loads(row['Geometry_ST'])
        coordinates = list(polygon.exterior.coords)
        state_id = row['State_Id']

        states = State.get_states_by_id()
        state = None
        if state_id in states:
            state = states[state_id]

        return cls(
            pid=row['Id'],
            object_id=row['ObjectId'],
            cap_city=row['CapCity'],
            state=state,
            source=row['Source'],
            shape_area=row['Shape_Area'],
            shape_length=row['Shape_Length'],
            geo_zone=row['Geo_Zone'],
            coordinates=coordinates,
            metadata=metadata,
        )

    def save_to_db(self, conn):
        """
        Save the GeoPolygon object to the database.

        Args:
            conn: Database connection object.
        """
        cursor = conn.cursor()
        try:
            insert_query = """
            INSERT INTO Polygon_Referenced_By_State (ObjectId, CapCity, Source, State_Id,
                                     Shape_Area, Shape_Length, Geo_Zone, Coordinates, Metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s), %s)
            """

            metadata_str = json.dumps(self.metadata)
            sid = ''
            if self.state is not None:
                sid = self.state.sid
            cursor.execute(insert_query, (
                self.object_id, self.cap_city,
                self.source, sid, self.shape_area, self.shape_length, self.geo_zone,
                PolygonReferencedByState.coordinates_to_wkt_polygon(self.coordinates),
                metadata_str
            ))
            conn.commit()
            print("GeoPolygon saved successfully!")

        except Exception as e:
            print(f"Error saving GeoPolygon: {e}")

        finally:
            cursor.close()

    @staticmethod
    def coordinates_to_wkt_polygon(coordinates):
        """
        Convert a list of coordinates into a WKT polygon string.

        Args:
            coordinates (list of tuples): List of (longitude, latitude) coordinates.

        Returns:
            str: WKT representation of the polygon.
        """
        polygon = Polygon(coordinates)
        wkt_polygon = polygon.wkt
        return wkt_polygon

    @staticmethod
    def batch_insert_geopolygon(conn, polygons):
        """
        Batch insert a list of GeoPolygon objects into the database.

        Args:
            conn: Database connection object.
            polygons (list of PolygonReferencedByState): List of GeoPolygon objects to insert.
        """
        cursor = conn.cursor()
        try:
            insert_query = """
            INSERT INTO Polygon_Referenced_By_State (ObjectId, CapCity, Source, State_Id,
                                     Shape_Area, Shape_Length, Geo_Zone, Coordinates, Metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s), %s)
            """

            data = [(gp.object_id, gp.cap_city,
                     gp.source, gp.state.sid if gp.state is not None else None, gp.shape_area, gp.shape_length,
                     gp.geo_zone, PolygonReferencedByState.coordinates_to_wkt_polygon(gp.coordinates),
                     json.dumps(gp.metadata))
                    for gp in polygons]

            cursor.executemany(insert_query, data)
            conn.commit()
            print(f"{cursor.rowcount} GeoPolygons inserted successfully!")

        except Exception as e:
            print(f"Error batch inserting GeoPolygons: {e}")

        finally:
            cursor.close()

    @staticmethod
    def find_polygon_by_point(conn, longitude, latitude):
        """
        Find a polygon containing a given point (longitude, latitude).

        Args:
            conn: Database connection object.
            longitude (float): Longitude of the point.
            latitude (float): Latitude of the point.

        Returns:
            PolygonReferencedByState: GeoPolygon object containing the point, or None if not found.
        """
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT *, ST_AsText(Coordinates) AS Geometry_ST
            FROM Polygon_Referenced_By_State
            WHERE ST_Contains(Coordinates, POINT(%s, %s))
            """

            cursor.execute(query, (longitude, latitude))
            row = cursor.fetchone()
            if row:
                return PolygonReferencedByState.from_db_row(row)
            else:
                print(f"No polygon contains point ({longitude}, {latitude})")
                return None

        except Exception as e:
            print(f"Error finding polygon by point: {e}")
            return None

        finally:
            cursor.close()

    @staticmethod
    def find_polygons_by_state(conn, states):
        """
        Find polygons belonging to a specific state.

        Args:
            conn: Database connection object.
            states (list): List of states.

        Returns:
            list: List of GeoPolygon objects belonging to the specified state.
        """
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT gp.*, ST_AsText(Coordinates) AS Geometry_ST FROM Polygon_Referenced_By_State gp
            LEFT JOIN State AS s ON gp.State_Id = s.Id
            WHERE s.Code IN ({})
            """.format(', '.join(['%s'] * len(states)))

            # Execute the query with the tuple of states
            cursor.execute(query, states)
            rows = cursor.fetchall()
            polygons = [PolygonReferencedByState.from_db_row(row) for row in rows]
            return polygons

        except Exception as e:
            print(f"Error finding polygons by state: {e}")
            return []

        finally:
            cursor.close()

    @staticmethod
    def get_all_polygons(conn):
        """
        Get all polygons.

        Args:
            conn: Database connection object.

        Returns:
            list: List of all GeoPolygon objects.
        """
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT *, ST_AsText(Coordinates) AS Geometry_ST FROM Polygon_Referenced_By_State
            """

            # Execute the query with the tuple of states
            cursor.execute(query)
            rows = cursor.fetchall()
            polygons = [PolygonReferencedByState.from_db_row(row) for row in rows]
            return polygons

        except Exception as e:
            print(f"Error finding polygons by state: {e}")
            return []

        finally:
            cursor.close()

    def __repr__(self):
        """
        Return a string representation of the GeoPolygon object.

        Returns:
            str: String representation of the GeoPolygon object.
        """
        return f"<PolygonReferencedByState(Id={self.id}, State={self.state}, Coordinates={self.coordinates})>"
