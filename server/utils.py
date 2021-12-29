import pymongo as mongo
from geojson import Feature, FeatureCollection, dump
from os.path import join
import hashlib
import folium
from folium import FeatureGroup
import geopandas as gpd


style_config = {
    "ОАП": "#0000FF",
    "osm": "orange"
}


def str_to_hash(input_str):
    return hashlib.md5(input_str.encode()).hexdigest()


class MongoGeoJSON:

    def __init__(self, host='192.168.57.119', port=27017, db_name='region63_samarskaya_obl'):
        self.client = mongo.MongoClient(host, port)
        self.db_name = db_name
        self.db = self.client[self.db_name]

    def create_geojson(self, collection_name, block_name, path="files/"):
        collection = self.db[collection_name]

        if collection_name == 'h_results':
            layer_name = 'ОАП'
        else:
            layer_name = collection_name.split('_')[0]

        if collection_name == 'h_results':
            filter = {"block": block_name}
        else:
            db = self.client['rk_metadata']
            col = db['regionBlocks']
            filter = col.find_one({'name': block_name})["filters"][layer_name]['filter']
            print(filter)

        results = collection.find(filter)

        features = []
        for row in results:
            if row['Geometry'] is not None:
                features.append(Feature(geometry=row['Geometry'],
                                        properties={'Municipalitet': row['Municipalitet'], 'Street': row['Street'],
                                                    'HouseNumber': row['HouseNumber']}))

        feature_collection = FeatureCollection(features)

        file_path = join(path, f'{collection_name}_{str_to_hash(block_name)}.geojson')
        with open(file_path, 'w') as f:
            dump(feature_collection, f)

        return layer_name, file_path


# def create_html(layers, block_name, path_to_save='files'):
#     _, filename = layers[0]
#     m = folium.Map(location=[53.050285598229, 49.7897474968519])
#     for layer in layers:
#         style_function = lambda x: {'color': style_config[layer[0]]}
#         print(style_config[layer[0]])
#         feature_group = FeatureGroup(name=layer[0])
#         folium.GeoJson(layer[1], name="geojson",
#                        popup=folium.GeoJsonPopup(fields=['Municipalitet', 'Street', 'HouseNumber']),
#                        marker=folium.CircleMarker(radius=3, fill=True),
#                        style_function=style_function).add_to(feature_group)
#         feature_group.add_to(m)
#     folium.LayerControl().add_to(m)
#     m.save(join(path_to_save, f"map_{str_to_hash(block_name)}.html"))


def create_html(layers, block_name, tiles, path_to_save='files'):
    df = gpd.read_file(layers[0][1])
    df = df.head(1)
    df["lon"] = df["geometry"].centroid.x
    df["lat"] = df["geometry"].centroid.y
    print(float(df["lat"]), float(df["lon"]))
    new_tiles = tiles
    if tiles != "OpenStreetMap":
        new_tiles = 'http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}'
    m = folium.Map(location=[float(df["lat"]), float(df["lon"])], zoom_start=15, tiles=new_tiles, attr='Google')
    style_function1 = lambda x: {'color': style_config[layers[0][0]]}
    style_function2 = lambda x: {'color': style_config[layers[1][0]]}
    print(style_config[layers[0][0]])
    feature_group1 = FeatureGroup(name=layers[0][0])
    folium.GeoJson(layers[0][1], name="geojson",
                   popup=folium.GeoJsonPopup(fields=['Municipalitet', 'Street', 'HouseNumber']),
                   marker=folium.CircleMarker(radius=3, fill=True),
                   style_function=style_function1).add_to(feature_group1).add_to(feature_group1)
    feature_group1.add_to(m)
    feature_group2 = FeatureGroup(name=layers[1][0])
    folium.GeoJson(layers[1][1], name="geojson",
                   popup=folium.GeoJsonPopup(fields=['Municipalitet', 'Street', 'HouseNumber']),
                   marker=folium.CircleMarker(radius=3, fill=True),
                   style_function=style_function2).add_to(feature_group2).add_to(feature_group2)
    feature_group2.add_to(m)
    folium.LayerControl().add_to(m)

    result_file = join(path_to_save, f"map_{str_to_hash(block_name)}.html")
    m.save(result_file)

    return result_file