USE map_db;

DROP TABLE IF EXISTS Geo_Polygon;

CREATE TABLE Geo_Polygon
(
    Id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    ObjectId     BIGINT       NULL,
    StateCode    VARCHAR(2)   NULL,
    `State`      VARCHAR(50)  NULL,
    CapCity      VARCHAR(50)  NULL,
    `Source`     VARCHAR(255) NULL,
    Shape_Area   FLOAT        NULL,
    Shape_Length FLOAT        NULL,
    Geo_Zone     VARCHAR(50)  NULL,
    `Timestamp`  DATETIME     NULL,
    Created_At   DATETIME     NULL,
    Updated_At   DATETIME     NULL,
    Coordinates  GEOMETRY     NOT NULL,
    Metadata     LONGTEXT     NULL
);
