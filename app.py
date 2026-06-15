# app.py
from flask import Flask, send_from_directory
from flask_cors import CORS
from api.students import students_bp
from api.attendance import attendance_bp
import os

app = Flask(__name__, static_folder='static')
CORS(app)

app.register_blueprint(students_bp,   url_prefix='/api/students')
app.register_blueprint(attendance_bp, url_prefix='/api/attendance')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/health')
def health():
    from datetime import datetime
    return {'status': 'ok', 'message': 'AbsensiAI berjalan', 'time': str(datetime.now())}

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
