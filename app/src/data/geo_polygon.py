import json
from shapely.geometry import Polygon
import shapely.wkt as wkt


class GeoPolygon:

    def __init__(self, pid=None, object_id=None, state_code=None, state=None, cap_city=None, source=None,
                 shape_area=None, shape_length=None, geo_zone=None, timestamp=None, created_at=None, updated_at=None,
                 coordinates=None, metadata=None):
        """
        Initialize a GeoPolygon object.

        Args:
            pid (int): Polygon ID.
            object_id (str): Object ID.
            state_code (str): State code.
            state (str): State name.
            cap_city (str): Capital city.
            source (str): Source of data.
            shape_area (float): Area of the polygon.
            shape_length (float): Perimeter of the polygon.
            geo_zone (str): Geographical zone.
            timestamp (str): Timestamp.
            created_at (str): Creation timestamp.
            updated_at (str): Last update timestamp.
            coordinates (list of tuples): List of (longitude, latitude) coordinates defining the polygon.
            metadata (dict): Additional metadata associated with the polygon.
        """
        self.id = pid
        self.object_id = object_id
        self.state_code = state_code
        self.state = state
        self.cap_city = cap_city
        self.source = source
        self.shape_area = shape_area
        self.shape_length = shape_length
        self.geo_zone = geo_zone
        self.timestamp = timestamp
        self.created_at = created_at
        self.updated_at = updated_at
        self.coordinates = coordinates
        self.metadata = metadata

    @classmethod
    def from_db_row(cls, row):
        """
        Create a GeoPolygon object from a database row.

        Args:
            row (dict): Database row containing polygon data.

        Returns:
            GeoPolygon: Initialized GeoPolygon object.
        """
        metadata = json.loads(row['Metadata'])
        polygon = wkt.loads(row['Geometry_ST'])
        coordinates = list(polygon.exterior.coords)
        return cls(
            pid=row['Id'],
            object_id=row['ObjectId'],
            state_code=row['StateCode'],
            state=row['State'],
            cap_city=row['CapCity'],
            source=row['Source'],
            shape_area=row['Shape_Area'],
            shape_length=row['Shape_Length'],
            geo_zone=row['Geo_Zone'],
            timestamp=row['Timestamp'],
            created_at=row['Created_At'],
            updated_at=row['Updated_At'],
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
            INSERT INTO Geo_Polygon (ObjectId, StateCode, State, CapCity, Source,
                                     Shape_Area, Shape_Length, Geo_Zone,
                                     Timestamp, Created_At, Updated_At, Coordinates, Metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s), %s)
            """

            metadata_str = json.dumps(self.metadata)
            cursor.execute(insert_query, (
                self.object_id, self.state_code, self.state, self.cap_city,
                self.source, self.shape_area, self.shape_length, self.geo_zone,
                self.timestamp, self.created_at, self.updated_at,
                GeoPolygon.coordinates_to_wkt_polygon(self.coordinates),
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
            polygons (list of GeoPolygon): List of GeoPolygon objects to insert.
        """
        cursor = conn.cursor()
        try:
            insert_query = """
            INSERT INTO Geo_Polygon (ObjectId, StateCode, State, CapCity, Source,
                                     Shape_Area, Shape_Length, Geo_Zone,
                                     Timestamp, Created_At, Updated_At, Coordinates, Metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s), %s)
            """

            data = [(gp.object_id, gp.state_code, gp.state, gp.cap_city,
                     gp.source, gp.shape_area, gp.shape_length, gp.geo_zone,
                     gp.timestamp, gp.created_at, gp.updated_at,
                     GeoPolygon.coordinates_to_wkt_polygon(gp.coordinates),
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
            GeoPolygon: GeoPolygon object containing the point, or None if not found.
        """
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
            SELECT *, ST_AsText(Coordinates) AS Geometry_ST
            FROM Geo_Polygon
            WHERE ST_Contains(Coordinates, POINT(%s, %s))
            """

            cursor.execute(query, (longitude, latitude))
            row = cursor.fetchone()
            if row:
                return GeoPolygon.from_db_row(row)
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
            SELECT *, ST_AsText(Coordinates) AS Geometry_ST FROM Geo_Polygon
            WHERE State IN ({})
            """.format(', '.join(['%s'] * len(states)))

            # Execute the query with the tuple of states
            cursor.execute(query, states)
            rows = cursor.fetchall()
            polygons = [GeoPolygon.from_db_row(row) for row in rows]
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
            SELECT *, ST_AsText(Coordinates) AS Geometry_ST FROM Geo_Polygon
            """

            # Execute the query with the tuple of states
            cursor.execute(query)
            rows = cursor.fetchall()
            polygons = [GeoPolygon.from_db_row(row) for row in rows]
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
        return f"<GeoPolygon(Id={self.id}, State={self.state}, Coordinates={self.coordinates})>"
