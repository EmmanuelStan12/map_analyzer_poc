from shapely import wkt

from app.src.map.data.polygon_referenced_by_state import PolygonReferencedByState


class PolygonReferencedByCountry:

    def __init__(self, pid=None, shape_area=None, shape_length=None, coordinates=None):
        self.pid = pid
        self.shape_area = shape_area
        self.shape_length = shape_length
        self.coordinates = coordinates

    @classmethod
    def from_db_row(cls, row):
        polygon = wkt.loads(row['Geometry_ST'])
        coordinates = list(polygon.exterior.coords)
        return cls(
            pid=row['Id'],
            shape_area=row['Shape_Area'],
            shape_length=row['Shape_Length'],
            coordinates=coordinates
        )

    def save_to_db(self, conn):
        cursor = conn.cursor()
        try:
            insert_query = """
                INSERT INTO Polygon_Referenced_By_Country (Shape_Area, Shape_Length, Coordinates)
                VALUES (%s, %s, ST_GeomFromText(%s))
            """

            cursor.execute(insert_query, (self.shape_area, self.shape_length,
                                          PolygonReferencedByState.coordinates_to_wkt_polygon(self.coordinates),
                                          ))
            conn.commit()
            print("GeoPolygon saved successfully!")

        except Exception as e:
            print(f"Error saving GeoPolygon: {e}")

        finally:
            cursor.close()

    @staticmethod
    def batch_insert_geopolygon(conn, polygons):
        cursor = conn.cursor()
        try:
            insert_query = """
                INSERT INTO Polygon_Referenced_By_Country (Shape_Area, Shape_Length, Coordinates)
                VALUES (%s, %s, ST_GeomFromText(%s))
            """

            data = [(gp.shape_area, gp.shape_length, PolygonReferencedByState.coordinates_to_wkt_polygon(gp.coordinates)) for gp in polygons]

            cursor.executemany(insert_query, data)
            conn.commit()
            print(f"{cursor.rowcount} GeoPolygons inserted successfully!")

        except Exception as e:
            print(f"Error batch inserting GeoPolygons: {e}")

        finally:
            cursor.close()

    @staticmethod
    def find_polygon_by_point(conn, longitude, latitude):
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT *, ST_AsText(Coordinates) AS Geometry_ST
                FROM Polygon_Referenced_By_Country
                WHERE ST_Contains(Coordinates, POINT(%s, %s))
            """

            cursor.execute(query, (longitude, latitude))
            row = cursor.fetchone()
            if row:
                return PolygonReferencedByCountry.from_db_row(row)
            else:
                print(f"No polygon contains point ({longitude}, {latitude})")
                return None

        except Exception as e:
            print(f"Error finding polygon by point: {e}")
            return None

        finally:
            cursor.close()

    @staticmethod
    def get_all_polygons(conn):
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT *, ST_AsText(Coordinates) AS Geometry_ST FROM Polygon_Referenced_By_Country
            """

            # Execute the query with the tuple of states
            cursor.execute(query)
            rows = cursor.fetchall()
            polygons = [PolygonReferencedByCountry.from_db_row(row) for row in rows]
            return polygons

        except Exception as e:
            print(f"Error finding polygons by country: {e}")
            return []

        finally:
            cursor.close()

    def __repr__(self):
        return f"<PolygonReferencedByCountry(Id={self.pid}, Coordinates={self.coordinates})>"
