from flask import Flask
from flask import request, send_file
import json
from utils import *

HOST, PORT = '0.0.0.0', 8080

app = Flask(__name__)

collections = ['h_results', 'osm_houses']


@app.get('/static')
def send_static():
    filename = "index.html"
    print("yes")
    return send_file(f'files/{filename}')


@app.post('/test_json')
def test_json():
    request_data = request.get_json()
    print(type(request_data))
    data_json = json.loads(request_data)
    print(data_json)
    mongo = MongoGeoJSON()
    layers = []
    for collection in collections:
        layer_name, file_path = mongo.create_geojson(collection, data_json["block_name"])
        layers.append((layer_name, file_path))

    print(layers)

    result_file = create_html(layers, data_json["block_name"], data_json["tiles"])

    return send_file(result_file)


if __name__ == '__main__':
    app.run(HOST, PORT, debug=True)