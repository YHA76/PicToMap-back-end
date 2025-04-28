from flask import Flask, request, jsonify
from flask_cors import CORS
import exifread
from io import BytesIO

app = Flask(__name__)
CORS(app)

def get_gps_coords(tags):
    try:
        gps_latitude = tags['GPS GPSLatitude'].values
        gps_latitude_ref = tags['GPS GPSLatitudeRef'].values[0]
        gps_longitude = tags['GPS GPSLongitude'].values
        gps_longitude_ref = tags['GPS GPSLongitudeRef'].values[0]

        def convert_to_degrees(values):
            d = float(values[0].num) / float(values[0].den)
            m = float(values[1].num) / float(values[1].den)
            s = float(values[2].num) / float(values[2].den)
            return d + (m / 60.0) + (s / 3600.0)

        lat = convert_to_degrees(gps_latitude)
        if gps_latitude_ref != 'N':
            lat = -lat

        lon = convert_to_degrees(gps_longitude)
        if gps_longitude_ref != 'E':
            lon = -lon

        return lat, lon
    except:
        return None, None

@app.route('/extract-gps', methods=['POST'])
def extract_gps():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    tags = exifread.process_file(file, details=False)

    lat, lon = get_gps_coords(tags)
    if lat is None or lon is None:
        return jsonify({'error': 'No GPS data found'}), 404

    return jsonify({'latitude': lat, 'longitude': lon}), 200

if __name__ == '__main__':
    app.run(debug=True)
