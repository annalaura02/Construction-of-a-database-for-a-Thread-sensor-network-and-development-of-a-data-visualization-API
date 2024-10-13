# Construction of a database for a Thread sensor network and development of a data visualization API

This repository contains the source code and documentation for the Sensor Network for Precision Agriculture project. The project leverages a Thread-based sensor network to monitor environmental conditions in agricultural fields, providing real-time data visualization and actionable insights to optimize crop management.

**Project Overview**
The system collects key environmental metrics such as:

Soil temperature
Humidity
pH levels
Infrared and visible light radiation
These metrics are collected using Thread-connected sensors and stored in a MySQL database. The data is accessed and visualized through a RESTful API, with an interactive PyQt6 GUI allowing users to monitor conditions in real time, generate graphs, and map optimal planting positions.

**Features**
Sensor Data Collection: Simulated sensor data generation using Python to replicate real-world agricultural conditions.

Database Management: Efficient MySQL database design optimized for fast data storage and querying.

API: A RESTful API built with Flask for seamless communication between sensors, database, and front-end tools.

Data Visualization: Interactive maps (Folium) and dynamic graphs (Matplotlib) to help users visualize environmental trends.

Plant Positioning Algorithm: Calculates the optimal planting position based on environmental conditions.
