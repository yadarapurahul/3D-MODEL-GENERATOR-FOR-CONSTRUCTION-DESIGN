from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from database import register_user, get_user_by_email, update_user_password, update_user_profile, revoke_token, is_token_revoked, get_dashboard_data, save_blueprint
from werkzeug.security import check_password_hash
from flask_jwt_extended.exceptions import NoAuthorizationError 
import logging
import os
import json
from datetime import datetime
import mimetypes

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
jwt = JWTManager()

from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_jwt_extended import exceptions as jwt_exceptions

@auth_bp.errorhandler(NoAuthorizationError)
def handle_auth_error(e):
    logger.error(f"Authorization error: {str(e)}")
    return jsonify({'message': 'Missing or invalid token'}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    logger.error("Expired token")
    return jsonify({'message': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    logger.error(f"Invalid token: {error_string}")
    return jsonify({'message': 'Invalid token'}), 422

@jwt.unauthorized_loader
def missing_token_callback(error_string):
    logger.error(f"Missing token: {error_string}")
    return jsonify({'message': 'Request does not contain an access token'}), 401

@jwt.needs_fresh_token_loader
def needs_fresh_token_callback(jwt_header, jwt_payload):
    logger.error("Fresh token required")
    return jsonify({'message': 'Fresh token required'}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    logger.error("Token has been revoked")
    return jsonify({'message': 'Token has been revoked'}), 401

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    revoked = is_token_revoked(jti)
    logger.debug(f"Checking token {jti}: Revoked={revoked}")
    return revoked

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'core')

    if not email or not password:
        logger.warning("Missing email or password in register request")
        return jsonify({'message': 'Email and password are required'}), 400

    try:
        register_user(email, password, role)
        logger.info(f"User registered: {email}")
        return jsonify({'message': 'User registered successfully'}), 201
    except ValueError as e:
        logger.error(f"Registration failed: {str(e)}")
        return jsonify({'message': str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    logger.debug("Login request received")
    data = request.get_json()
    logger.debug(f"Login request data: {data}")
    email = data.get('email')
    password = data.get('password')

    try:
        user = get_user_by_email(email)
        logger.debug(f"User fetched for login: {user}")
        if user and check_password_hash(user[2], password):
            access_token = create_access_token(identity={'id': user[0], 'email': user[1], 'role': user[3]})
            logger.info(f"User logged in: {email}")
            logger.debug(f"Login token: {access_token}")
            return jsonify({'token': access_token}), 200
        logger.warning(f"Invalid login attempt for {email}")
        return jsonify({'message': 'Invalid credentials'}), 401
    except ValueError as e:
        logger.error(f"Login failed: {str(e)}")
        return jsonify({'message': str(e)}), 400

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        jti = get_jwt()['jti']
        revoke_token(jti)
        logger.info(f"Token revoked: {jti}")
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        return jsonify({'message': 'Logout failed'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    try:
        user = get_user_by_email(email)
        if user:
            token = create_access_token(identity={'id': user[0], 'email': user[1]})
            logger.info(f"Password reset requested for {email}")
            return jsonify({'message': 'Reset link sent to email'}), 200
        logger.warning(f"Email not found: {email}")
        return jsonify({'message': 'Email not found'}), 404
    except ValueError as e:
        logger.error(f"Forgot password failed: {str(e)}")
        return jsonify({'message': str(e)}), 400

@auth_bp.route('/reset-password', methods=['POST'])
@jwt_required()
def reset_password():
    data = request.get_json()
    password = data.get('password')
    identity = get_jwt_identity()

    try:
        update_user_password(identity['id'], password)
        logger.info(f"Password reset for user ID {identity['id']}")
        return jsonify({'message': 'Password reset successfully'}), 200
    except ValueError as e:
        logger.error(f"Password reset failed: {str(e)}")
        return jsonify({'message': str(e)}), 400

@auth_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    identity = get_jwt_identity()

    try:
        if request.method == 'GET':
            user = get_user_by_email(identity['email'])
            if user:
                logger.debug(f"Profile fetched for {identity['email']}")
                return jsonify({'email': user[1], 'role': user[3]}), 200
            logger.warning(f"User not found: {identity['email']}")
            return jsonify({'message': 'User not found'}), 404

        if request.method == 'PUT':
            data = request.get_json()
            password = data.get('password')
            role = data.get('role')
            update_user_profile(identity['id'], password, role)
            logger.info(f"Profile updated for user ID {identity['id']}")
            return jsonify({'message': 'Profile updated successfully'}), 200
    except ValueError as e:
        logger.error(f"Profile operation failed: {str(e)}")
        return jsonify({'message': str(e)}), 400

@auth_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    try:
        auth_header = request.headers.get('Authorization')
        logger.debug(f"Authorization header received: {auth_header}")
        identity = get_jwt_identity()
        logger.debug(f"Fetching dashboard for user ID {identity['id']}")
        dashboard_data = get_dashboard_data(identity['id'])
        if dashboard_data:
            logger.info(f"Dashboard data sent for {identity['email']}")
            return jsonify(dashboard_data), 200
        logger.warning(f"User not found for dashboard: {identity['email']}")
        return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Dashboard request failed: {str(e)}")
        return jsonify({'message': f'Failed to load dashboard: {str(e)}'}), 500

@auth_bp.route('/blueprint/upload', methods=['POST'])
@jwt_required()
def upload_blueprint():
    identity = get_jwt_identity()
    user = get_user_by_email(identity['email'])
    if not user or user[3] != 'admin':
        logger.warning(f"Unauthorized blueprint upload attempt by {identity['email']}")
        return jsonify({'message': 'Admin access required'}), 403

    if 'blueprint' not in request.files:
        logger.warning(f"No file in blueprint upload request by {identity['email']}")
        return jsonify({'message': 'No file part'}), 400
    file = request.files['blueprint']
    if file.filename == '':
        logger.warning(f"No selected file by {identity['email']}")
        return jsonify({'message': 'No selected file'}), 400

    # Validate file extension and MIME type
    valid_extensions = ['.pdf', '.jpg', '.jpeg']
    valid_mimes = ['application/pdf', 'image/jpeg']
    filename = file.filename.lower()
    mime_type, _ = mimetypes.guess_type(filename)
    if not any(filename.endswith(ext) for ext in valid_extensions) or mime_type not in valid_mimes:
        logger.warning(f"Invalid file type by {identity['email']}: {filename}")
        return jsonify({'message': 'Only PDF or JPG files are allowed'}), 400

    try:
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, f"{identity['id']}_{datetime.now().timestamp()}_{file.filename}")
        file.save(filepath)
        # Placeholder dimensions; replace with actual parsing logic for 3D conversion
        dimensions = json.dumps({'x': 10, 'y': 20, 'z': 30})
        blueprint_id = save_blueprint(identity['id'], file.filename, filepath, dimensions, 'none')
        logger.info(f"Blueprint uploaded for conversion by {identity['email']}: {file.filename}")
        return jsonify({'message': 'Blueprint uploaded successfully, conversion in progress', 'blueprint_id': blueprint_id}), 200
    except Exception as e:
        logger.error(f"Blueprint upload failed: {str(e)}")
        return jsonify({'message': f'Upload failed: {str(e)}'}), 500