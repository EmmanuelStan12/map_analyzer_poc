# Map Analyzer Proof of Concept

This project demonstrates the handling and visualization of geospatial data using Python. It involves creating, manipulating, and storing polygon geometries, and visualizing them on an interactive map.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Setting Up the Environment](#setting-up-the-environment)
- [Why Python?](#why-python)
- [Terminologies](#terminologies)
    - [CRS (Coordinate Reference System)](#crs-coordinate-reference-system)
    - [GeoDataFrame](#geodataframe)
    - [Pandas](#pandas)
    - [GeoPandas](#geopandas)
    - [Folium](#folium)
    - [Shapely](#shapely)
- [Project Structure](#project-structure)
- [GeoPolygon Data Structure](#geopolygon-data-structure)
- [Usage](#usage)

## Introduction

The GeoPolygon project is designed to work with geospatial data, specifically polygons representing regions on a map. The project includes functionality for reading GeoJSON files, creating grid overlays, clipping grids to regions, and saving these geometries to a database. Additionally, it provides visualization of these geometries using Folium to create interactive maps.

## Installation

1. **Install Python:**
    - Download and install Python from the official website: [Python Downloads](https://www.python.org/downloads/).

2. **Set up a virtual environment (Optional):**
    - Create a virtual environment:
      ```bash
      python -m venv venv
      ```
    - Activate the virtual environment:
        - On Windows:
          ```bash
          venv\\Scripts\\activate
          ```
        - On macOS/Linux:
          ```bash
          source venv/bin/activate
          ```

3. **Install the required libraries:**
    - Install the necessary Python packages using `pip`:
      ```bash
      pip install geopandas shapely folium pandas mysql-connector-python lxml pykml python-dotenv
      ```

## Setting Up the Environment

To run the project, you need a working Python environment with the necessary libraries installed. Ensure you have a MySQL database set up with the required table schema to store the polygon data.

## Why Python?

Python is the preferred language for this proof of concept due to its rich ecosystem of libraries for data analysis and visualization. Libraries such as Pandas, GeoPandas, and Folium make it easy to manipulate geospatial data and create interactive visualizations. Additionally, Python's simplicity and readability make it an ideal choice for prototyping and developing data-centric applications.

## Terminologies

### CRS (Coordinate Reference System)

A Coordinate Reference System (CRS) defines how the two-dimensional, projected map in your GeoDataFrame relates to real places on the earth. Commonly used CRSs include:
- **WGS84 (EPSG:4326)**: The standard for GPS coordinates.
- **Web Mercator (EPSG:3857)**: Used by most web mapping applications like Google Maps.

### GeoDataFrame

A GeoDataFrame is a data structure in GeoPandas, an extension of Pandas, designed to handle geospatial data. It contains a geometry column that stores geometric shapes (points, lines, polygons) along with other data.

### Pandas

Pandas is a powerful data manipulation library in Python. It provides data structures like DataFrame, which is used to store and manipulate tabular data.

### GeoPandas

GeoPandas extends Pandas to allow spatial operations on geometric types. It enables reading, writing, and analyzing geospatial data.

### Folium

Folium is a Python library used for creating interactive maps. It allows you to visualize geospatial data by rendering it on a Leaflet.js map, which can be displayed in a web browser.

### Shapely

Shapely is a Python library for manipulation and analysis of planar geometric objects. It provides functionalities to create and work with points, lines, and polygons.

The project "map_analyzer_poc" has been extracted. Here's a detailed overview and explanation of the project, including the algorithms and how everything is implemented.

### Project Structure

The project is structured as follows:

```
map_analyzer_poc-master/
├── .env_example
├── .gitignore
├── README.md
└── app/
    └── src/
        ├── data/
        │   ├── ddl.sql
        │   ├── nigeria_state_dml.sql
        │   ├── polygon_referenced_by_country.py
        │   ├── polygon_referenced_by_state.py
        │   └── state.py
        ├── export.py
        ├── extract.py
        ├── grid.py
        ├── main.py
        ├── plot.py
        ├── polygon.py
        └── reader.py
```

### Files and Their Functions

#### 1. `.env_example`
This file is likely used to provide an example of environment variables that need to be set for the project to run correctly.

#### 2. `.gitignore`
This file specifies files and directories that should be ignored by git. Common entries might include logs, temporary files, and environment variable files.

#### 3. `README.md`
This file provides an overview of the project, its purpose, and how to set it up. It usually includes instructions on how to install dependencies, run the project, and any other relevant information.

#### 4. `app/src/`
This directory contains the main source code for the project.

##### a. `data/`
This subdirectory includes scripts and files related to data handling:

- `ddl.sql` and `nigeria_state_dml.sql`: These files contain SQL scripts for data definition and data manipulation, respectively. They are used to create and populate the database tables.
- `polygon_referenced_by_country.py`, `polygon_referenced_by_state.py`, `state.py`: These files contain Python classes that represent different entities in the project.

##### b. `export.py`
This script handles exporting data from the application to various formats, such as KML or GeoJSON.

##### c. `extract.py`
This script is responsible for extracting relevant data from input sources. It likely includes functions to parse and extract data from GeoJSON files or other spatial data formats.

##### d. `grid.py`
This script manages the creation of grids on maps. It includes functions to create grid cells and assign spatial data to these cells.

##### e. `main.py`
The main entry point of the application. This script initializes the application and orchestrates the execution of other scripts.

##### f. `plot.py`
This script handles plotting and visualization of spatial data. It includes functions to generate maps and other visual representations of the data.

##### g. `polygon.py`
This script includes functions and classes for handling polygon geometries, including creation, manipulation, and validation of polygons.

##### h. `reader.py`
This script includes functions to read and parse GeoJSON input files.

## GeoPolygon Data Structure

### Database Table: `Polygon_Referenced_By_State`, `Polygon_Referenced_By_Country` and `State`

The `State` table is designed to store state metadata for a certain country.

```sql
CREATE TABLE State
(
    Id   BIGINT AUTO_INCREMENT PRIMARY KEY,
    Code VARCHAR(10)  NOT NULL,
    Name VARCHAR(100) NOT NULL
);
```

The `Polygon_Referenced_By_State` table is designed to store polygon data for geographical regions where the clipping respects the state boundaries. Here is the SQL schema for the table:

```sql
CREATE TABLE Polygon_Referenced_By_State
(
    Id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    ObjectId     BIGINT       NULL,
    State_Id     BIGINT       NOT NULL,
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
```

The `Polygon_Referenced_By_Country` table is designed to store polygon data for geographical regions where the clipping respects the country's boundaries but ignores the state boundaries. Here is the SQL schema for the table:

```sql
CREATE TABLE Polygon_Referenced_By_Country
(
    Id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    Shape_Area   FLOAT        NULL,
    Shape_Length FLOAT        NULL,
    Coordinates  GEOMETRY     NOT NULL
);
```

### Explanation of the Structure

- Id: This is a unique identifier for each polygon. It is set to auto-increment, ensuring each entry gets a unique value.
- ObjectId: This field is used to store a secondary identifier, which can be useful for linking the polygon to other datasets or records.
- StateCode: This stores a two-letter code representing the state the polygon belongs to. It helps in quickly identifying the state.
- State: This field stores the full name of the state for human-readable purposes.
- CapCity: This stores the name of the capital city of the state, providing additional geographical context.
- Source: This field captures the source of the polygon data, which is important for data provenance and validation.
- Shape_Area: This stores the area of the polygon, which is useful for geographical and statistical analysis.
- Shape_Length: This stores the perimeter length of the polygon, providing another measure for geographical analysis.
- Geo_Zone: This field stores the geographical zone the polygon belongs to, allowing for regional analysis.
- Timestamp: This captures the time the polygon data was recorded or last modified, providing a historical context.
- Created_At: This stores the timestamp when the record was first created in the database.
- Updated_At: This stores the timestamp when the record was last updated.
- Coordinates: This is a geometry field that stores the actual polygon coordinates. It uses the GEOMETRY data type to efficiently handle spatial data and enables spatial queries.
- Metadata: This field stores additional metadata in JSON format, providing flexibility to store varied additional information that may not fit into the fixed schema.

### Reasons for the Chosen Structure
- Efficiency and Performance: The use of the GEOMETRY data type for the Coordinates field ensures that spatial data is stored and managed efficiently. This allows for fast and efficient spatial queries and operations.
- Flexibility: The inclusion of the Metadata field as a LONGTEXT type allows for flexible storage of additional information that may not be easily categorized into the other fixed fields. This can include details such as tags, notes, or additional attributes that might be required for different use cases.
- Data Integrity: Using specific data types like BIGINT for IDs and VARCHAR for strings ensures data integrity and appropriate storage allocation. The structure also ensures that important fields like Coordinates are not null, maintaining the integrity of the geographical data.
- Readability and Context: Fields like State, CapCity, and Geo_Zone provide human-readable context, making it easier to understand the geographical information without needing to decode or look up state codes or object IDs.
- Provenance and Traceability: The Source, Timestamp, Created_At, and Updated_At fields help in tracking the origin and changes to the data over time, which is crucial for data validation, auditing, and historical analysis.

This explanation and reasons for the chosen structure applies to the `Polygon_Referenced_By_State` and `Polygon_Referenced_By_Country` tables.

## Step-by-step Procedure

### Algorithm to Break Map into Squares and Save Polygons to MySQL

Here's a step-by-step algorithm for breaking the map into squares, calculating width and height, and saving each polygon in its MySQL entry:

#### Step 1: Read GeoJSON File
- Read the GeoJSON file containing the map data (Check `read_geojson(path)`).
- This returns a GeoDataFrame data structure.
- This can return a GeoDataFrame, which contains data relative to how the data desired, it could be relative to the state or country.
- When it is relative to the state, the data frame formed are more and have more boundaries that determine the borders of states in the map.
- However, if it is country, those boundaries are dissolved.

#### Step 2: Calculate Grid Parameters
- Determine the grid cell dimensions (width and height) based on the desired square size (e.g., 50 km).
- Use the latitude to calculate the approximate width and height in degrees (Check `kilometres_to_degrees(kilometres)`).

#### Step 3: Create Grid
- Create a rectangular grid over the bounding box of the GeoDataFrame.
- Use the calculated grid cell dimensions (in degrees) to define each grid cell (Check `create_grid(geo_df, grid_height, grid_width)`).

#### Step 4: Clip Grid with Map
- Clip the grid cells with the map to retain only the intersecting areas.
- This ensures that each grid cell corresponds to a valid geographic area within the map boundaries (Check `clip_grid(grid_geo_df, map_geo_df)`).

#### Step 5: Extract Polygons
- Extract polygons from the clipped grid GeoDataFrame.
- Convert each polygon into a GeoPolygon object, including its metadata and coordinates (Check `extract_polygons(geo_df, grid_height, grid_width, referenced_by_country)`).

#### Step 6: Save to MySQL
- Establish a connection to the MySQL database.
- Define an SQL schema that includes fields for storing polygon attributes and the geometry.
- Use SQL queries to insert each GeoPolygon object into the database, converting its coordinates to WKT format for storage (Check `<Polygon table>.batch_insert_geopolygon(conn, polygons)`).

### Additional Operations

- **Get Polygons Points or All:**
    - Retrieve polygons based on state codes, specific points, or fetch all polygons stored in the database(Check `<Polygon table>.find_polygon_by_point(conn, longitude, latitude)` and `<Polygon table>.get_all_polygons(conn)`).

- **Get Polygons by State:**
    - Retrieve polygons based on state codes stored in the database, this only applies to `Polygon_Referenced_By_State` (Check `<Polygon table>.find_polygons_by_state(conn, states)`).

- **Plot Polygons by Exporting as HTML:**
    - Utilize Folium to export polygons as interactive HTML maps for visualization (Check `plot_geo_dataframe(geo_df, output_file)`).

- **Export Polygons as KML:**
    - Implement functionality to export polygons as KML files for use in other mapping applications (Check `export_to_kml(polygons, file_path, grid_height, grid_width)`).

- **Export Polygons as GeoJSON:**
    - Implement functionality to export geo dataframes as GeoJSON file (Check `export_to_geojson(geo_df, file_path)`).

## Usage

### Pre-requisites

1. Ensure you have Python installed. If not, download it from [Python Downloads](https://www.python.org/downloads/).
2. Set up a virtual environment and activate it (Optional):
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3. Install required libraries:
    ```bash
    pip install geopandas shapely folium pandas mysql-connector-python lxml pykml python-dotenv
    ```
4. Set up MySQL database:
    - Create a database and execute the `ddl.sql` script to set up `State`, `Polygon_Referenced_By_State` and `Polygon_Referenced_By_Country` table schemas.
    - Execute `nigeria_state_dml.sql` to insert states into the `State` table schema.

5. Configure environment variables:
    - Copy `.env_example` to `.env` and adjust values as per your MySQL database configuration.

6. Review and run the Python scripts:
    - Uncomment `extract_and_save_geojson_file()` function if it's the first run to populate your database with initial data.
    - Ensure other functions such as polygon extraction, database operations, and visualizations are tailored to your needs.

### Running the Project

- Navigate to your project directory and execute `main.py` to initiate the operations defined in your scripts.
- Monitor console output for any errors or progress updates as the scripts execute.

### Notes

- Adjust grid size, polygon extraction logic, and visualization parameters as per your specific requirements and dataset characteristics.

### Error Margins

- Errors may be in the geojson, that is, it may not be as accurate as the map in Google Maps, so the error margin can be reduced by checking for more accurate geojson files for the country in study.
- Errors may also be in the `read_geojson` function when trying to read a file referencing it by country because the topologies of the geojson may be wrong, the code tries to correct some polygons in the map before returning the `GeoDataFrame`, if the tolerance value is not enough, you can research on better ways to correct the topology or better still, get a more accurate map geojson file.
- Errors may also be in the library reading the geojson file, which has not been researched, but the functionality is widely acceptable by millions of users.

## Conclusion

The Map Analyzer Proof of Concept project showcases the capabilities of Python and its libraries for geospatial data handling. By following the steps outlined in this README, you can effectively manage, manipulate, and visualize polygonal data, enhancing your understanding and analysis of geographic regions.

Feel free to reach out for further assistance or customization of this project!
