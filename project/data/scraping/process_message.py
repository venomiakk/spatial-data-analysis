import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import requests
from shapely.geometry import Point, Polygon, LineString, MultiLineString
import pandas as pd
import json
import geojson
import re

def process_feature_broutes(feature):
    # Extract coordinates
    coords = [(float(p['longitude']), float(p['latitude'])) 
             for p in feature['geometry']['coordinates']]
    # print(coords)
    # Create LineString
    line = LineString(coords)
    print(line)
    
    # Transform properties from key-value pairs to dictionary
    props = {}
    for prop in feature['properties']:
        props[prop['key']] = prop['value']
    
    return line, props

def create_broutes_gdf(json_file):
    # Read JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    lines = []
    properties = []
    
    # Process each feature
    for feature in data['featureMemberList']:
        line, props = process_feature_broutes(feature)
        lines.append(line)
        properties.append(props)
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        properties,
        geometry=lines,
        crs="EPSG:4326"
    )
    
    return gdf


bike_routes_gdf = create_broutes_gdf('..\\wwa_bikeroutes.json')