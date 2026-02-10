from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import ctypes
import os

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE = 'emergency_resources.db'

# Load C library for distance calculation
lib_path = './distance_calculator.so'  # For Linux
# lib_path = './distance_calculator.dylib'  # For macOS
# lib_path = './distance_calculator.dll'  # For Windows

if os.path.exists(lib_path):
    distance_lib = ctypes.CDLL(lib_path)
    distance_lib.haversine_distance.argtypes = [
        ctypes.c_double, ctypes.c_double,
        ctypes.c_double, ctypes.c_double
    ]
    distance_lib.haversine_distance.restype = ctypes.c_double
else:
    distance_lib = None
    print("Warning: C library not found. Using Python fallback.")


def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def calculate_distance_python(lat1, lon1, lat2, lon2):
    """Fallback Python implementation of Haversine formula"""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371.0  # Earth radius in kilometers
    
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance using C library or Python fallback"""
    if distance_lib:
        return distance_lib.haversine_distance(lat1, lon1, lat2, lon2)
    else:
        return calculate_distance_python(lat1, lon1, lat2, lon2)


@app.route('/api/resources', methods=['POST'])
def get_resources():
    """Get nearest emergency resources based on user location"""
    try:
        data = request.get_json()
        user_lat = data.get('latitude')
        user_lon = data.get('longitude')
        
        if user_lat is None or user_lon is None:
            return jsonify({'error': 'Invalid location data'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Fetch all resources
        cursor.execute('SELECT * FROM resources')
        resources = cursor.fetchall()
        conn.close()
        
        # Calculate distances and sort
        resources_with_distance = []
        for resource in resources:
            distance = calculate_distance(
                user_lat, user_lon,
                resource['latitude'], resource['longitude']
            )
            
            resources_with_distance.append({
                'id': resource['id'],
                'name': resource['name'],
                'type': resource['type'],
                'address': resource['address'],
                'phone': resource['phone'],
                'latitude': resource['latitude'],
                'longitude': resource['longitude'],
                'distance': distance
            })
        
        # Sort by distance
        resources_with_distance.sort(key=lambda x: x['distance'])
        
        return jsonify({
            'success': True,
            'user_location': {
                'latitude': user_lat,
                'longitude': user_lon
            },
            'resources': resources_with_distance[:10]  # Return top 10
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'c_library_loaded': distance_lib is not None
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
