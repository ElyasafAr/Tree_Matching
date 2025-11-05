import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, User
from utils import get_current_user_id
import cloudinary
import cloudinary.uploader
import cloudinary.api

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/profile-image', methods=['POST'])
@jwt_required()
def upload_profile_image():
    """Upload a profile image to Cloudinary"""
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
        
        # Delete old profile image from Cloudinary if exists
        if user.profile_image:
            try:
                # Extract public_id from URL
                # Format: dating_site/profiles/user_123
                public_id = user.profile_image
                cloudinary.uploader.destroy(public_id)
            except Exception as e:
                print(f"Error deleting old image: {e}")
                # Continue even if delete fails
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file,
            folder="dating_site/profiles",  # Organize in folders
            public_id=f"user_{current_user_id}",  # Consistent naming
            overwrite=True,  # Replace if exists
            resource_type="image",
            transformation=[
                {'width': 1200, 'height': 1200, 'crop': 'limit'},  # Max size
                {'quality': 'auto:good'},  # Auto quality
                {'fetch_format': 'auto'}  # Auto format (WebP when supported)
            ]
        )
        
        # Store the public_id (not the full URL) for flexibility
        public_id = upload_result['public_id']
        user.profile_image = public_id
        db.session.commit()
        
        # Return the optimized URL
        image_url = upload_result['secure_url']
        
        return jsonify({
            'message': 'Profile image uploaded successfully',
            'image_url': image_url,
            'public_id': public_id
        }), 200
        
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

# No longer needed - images served directly from Cloudinary CDN!

@upload_bp.route('/profile-image', methods=['DELETE'])
@jwt_required()
def delete_profile_image():
    """Delete user's profile image from Cloudinary"""
    try:
        current_user_id = get_current_user_id()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.profile_image:
            return jsonify({'error': 'No profile image to delete'}), 400
        
        # Delete from Cloudinary
        try:
            public_id = user.profile_image
            cloudinary.uploader.destroy(public_id)
        except Exception as e:
            print(f"Error deleting from Cloudinary: {e}")
            # Continue even if delete fails
        
        # Remove from database
        user.profile_image = None
        db.session.commit()
        
        return jsonify({'message': 'Profile image deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

