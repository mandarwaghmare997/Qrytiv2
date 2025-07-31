import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from src.models.user import db

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'qrytiv2-secret-key-2025'

# Enable CORS for all routes
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# API Health check
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Qrytiv2 API is running',
        'version': '2.0.0'
    })

# Sample API endpoints for the frontend
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    return jsonify({
        'message': 'Registration successful',
        'user': {
            'id': 1,
            'email': data.get('email', ''),
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', '')
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': 1,
            'email': data.get('email', ''),
            'first_name': 'Demo',
            'last_name': 'User',
            'role': 'admin'
        }
    }), 200

@app.route('/api/assessments', methods=['GET'])
def get_assessments():
    return jsonify([
        {
            'id': 1,
            'name': 'ISO 42001 Assessment',
            'status': 'in_progress',
            'overall_score': 73.5,
            'stages': [
                {'id': 1, 'name': 'Requirements Analysis', 'status': 'completed', 'progress': 100},
                {'id': 2, 'name': 'Gap Assessment', 'status': 'completed', 'progress': 100},
                {'id': 3, 'name': 'Policy Framework', 'status': 'in_progress', 'progress': 75},
                {'id': 4, 'name': 'Implementation', 'status': 'in_progress', 'progress': 45},
                {'id': 5, 'name': 'Validation & Testing', 'status': 'pending', 'progress': 0},
                {'id': 6, 'name': 'Certification', 'status': 'pending', 'progress': 0}
            ]
        }
    ])

# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

