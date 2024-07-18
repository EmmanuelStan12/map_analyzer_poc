# GeoPolygon Project

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

2. **Set up a virtual environment:**
    - Create a virtual environment:
      ```bash
      python -m venv venv
      ```
    - Activate the virtual environment (Optional):
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

## Project Structure

The project consists of three main files:

1. **geo_polygon.py**
    - Defines the `GeoPolygon` class for handling polygon geometries.
    - Contains methods for initializing objects, saving to the database, and retrieving from the database.

2. **main.py**
    - Entry point for the project.
    - Connects to the MySQL database and performs operations like extracting polygons and visualizing them.

3. **map.py**
    - Contains functions for reading GeoJSON files, creating grids, clipping grids, and exporting data to different formats.
    - Provides visualization functions using Folium.

## GeoPolygon Data Structure

### Database Table: Geo_Polygon

The `Geo_Polygon` table is designed to store polygon data for geographical regions. Here is the SQL schema for the table:

```sql
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

## Usage

1. **Setup Database Connection:**
    - Update the database connection details in `main.py` with your MySQL database credentials.

2. **Run the Project:**
    - To extract and save GeoJSON data to the database:
      ```bash
      python main.py
      ```
    - This will read a GeoJSON file, create a grid overlay, clip the grid to regions, and save the resulting polygons to the database.

3. **Visualize Data:**
    - The `main.py` script will also generate an interactive HTML map showing the polygons for specified states. Open the `output.html` file in a web browser to view the map.