import os
import secrets
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from models import db, User
from utils import get_current_user_id

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

# Configuration
UPLOAD_FOLDER = 'uploads/profile_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """Generate a unique filename to prevent collisions"""
    ext = filename.rsplit('.', 1)[1].lower()
    unique_name = secrets.token_urlsafe(16)
    return f"{unique_name}.{ext}"

@upload_bp.route('/profile-image', methods=['POST'])
@jwt_required()
def upload_profile_image():
    """Upload a profile image"""
    try:
        current_user_id = get_current_user_id()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File size exceeds maximum limit of {MAX_FILE_SIZE / (1024*1024)}MB'}), 400
        
        # Delete old profile image if exists
        if user.profile_image:
            old_image_path = os.path.join(UPLOAD_FOLDER, os.path.basename(user.profile_image))
            if os.path.exists(old_image_path):
                try:
                    os.remove(old_image_path)
                except:
                    pass  # Ignore errors when deleting old file
        
        # Save new file
        filename = generate_unique_filename(secure_filename(file.filename))
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Update user profile with new image URL
        image_url = f'/upload/profile-images/{filename}'
        user.profile_image = image_url
        db.session.commit()
        
        return jsonify({
            'message': 'Profile image uploaded successfully',
            'image_url': image_url
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/profile-images/<filename>', methods=['GET'])
def serve_profile_image(filename):
    """Serve profile images"""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        return jsonify({'error': 'Image not found'}), 404

@upload_bp.route('/profile-image', methods=['DELETE'])
@jwt_required()
def delete_profile_image():
    """Delete user's profile image"""
    try:
        current_user_id = get_current_user_id()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.profile_image:
            return jsonify({'error': 'No profile image to delete'}), 400
        
        # Delete file from filesystem
        image_path = os.path.join(UPLOAD_FOLDER, os.path.basename(user.profile_image))
        if os.path.exists(image_path):
            os.remove(image_path)
        
        # Remove from database
        user.profile_image = None
        db.session.commit()
        
        return jsonify({'message': 'Profile image deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

