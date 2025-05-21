from flask import Flask, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from auth import auth_bp
from database import init_db
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {
    "origins": "http://localhost:3000",
    "allow_headers": ["Authorization", "Content-Type"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
}})
app.config['JWT_SECRET_KEY'] = '046af5e1593f6a268efaaac3f11f9dbc65a62b6335bdd3ab21959856d5495631'
jwt = JWTManager(app)



# Initialize database
init_db()

# Register auth blueprint
app.register_blueprint(auth_bp, url_prefix='/api')

@app.route('/exports/<path:filename>')
def serve_exported_file(filename):
    try:
        return send_file(os.path.join('exports', filename))
    except FileNotFoundError:
        logger.error(f"Export file not found: {filename}")
        return jsonify({'message': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)