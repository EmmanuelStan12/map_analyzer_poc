USE map_db;

DROP TABLE IF EXISTS Polygon_Referenced_By_State;

DROP TABLE IF EXISTS State;

CREATE TABLE State
(
    Id   BIGINT AUTO_INCREMENT PRIMARY KEY,
    Code VARCHAR(10)  NOT NULL,
    Name VARCHAR(100) NOT NULL
);

CREATE TABLE Polygon_Referenced_By_State
(
    Id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    ObjectId     BIGINT       NULL,
    State_Id     BIGINT       NULL,
    CapCity      VARCHAR(50)  NULL,
    Source       VARCHAR(255) NULL,
    Shape_Area   FLOAT        NULL,
    Shape_Length FLOAT        NULL,
    Geo_Zone     VARCHAR(50)  NULL,
    Created_At   DATETIME     NULL,
    Updated_At   DATETIME     NULL,
    Coordinates  GEOMETRY     NOT NULL,
    Metadata     LONGTEXT     NULL,
    CONSTRAINT FOREIGN KEY (State_Id) REFERENCES State (Id)
);

DROP TABLE IF EXISTS Polygon_Referenced_By_Country;

CREATE TABLE Polygon_Referenced_By_Country
(
    Id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    Shape_Area   FLOAT        NULL,
    Shape_Length FLOAT        NULL,
    Coordinates  GEOMETRY     NOT NULL
);
