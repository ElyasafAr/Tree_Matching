from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, User, Match, Referral
from encryption import encryption_service
from utils import get_current_user_id
from sqlalchemy import or_, and_
import cloudinary
import cloudinary.utils
import os

users_bp = Blueprint('users', __name__, url_prefix='/users')

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

def get_cloudinary_url(public_id):
    """Convert Cloudinary public_id to full URL"""
    if not public_id:
        return None
    
    # If it's already a full URL, return it
    if public_id.startswith('http'):
        return public_id
    
    # Generate Cloudinary URL with optimizations
    return cloudinary.CloudinaryImage(public_id).build_url(
        secure=True,
        transformation=[
            {'quality': 'auto:good'},
            {'fetch_format': 'auto'}
        ]
    )

@users_bp.route('/profile/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    """Get user profile by ID"""
    try:
        print(f"[GET PROFILE] ========== START ==========")
        print(f"[GET PROFILE] Request received for user_id: {user_id}")
        current_user_id = get_current_user_id()
        print(f"[GET PROFILE] Current user ID: {current_user_id}")
        
        user = User.query.get(user_id)
        print(f"[GET PROFILE] User query result: {user}")
        
        if not user:
            print(f"[GET PROFILE] ❌ User not found for ID: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        # Basic user data
        user_data = user.to_dict()
        print(f"[GET PROFILE] user.social_link from DB: {user.social_link}")  # Debug log
        print(f"[GET PROFILE] user_data.social_link from to_dict: {user_data.get('social_link')}")  # Debug log
        
        # Decrypt full_name safely
        try:
            user_data['full_name'] = encryption_service.decrypt(user.full_name_encrypted)
        except Exception as e:
            print(f"[GET PROFILE] Error decrypting full_name: {e}")
            user_data['full_name'] = "שם לא זמין"
        
        # Convert Cloudinary public_id to full URL
        user_data['profile_image'] = get_cloudinary_url(user.profile_image)
        
        # Get referrer info
        try:
            referral = Referral.query.filter_by(referred_id=user.id).first()
            if referral:
                referrer = User.query.get(referral.referrer_id)
                if referrer:
                    try:
                        referrer_name = encryption_service.decrypt(referrer.full_name_encrypted)
                    except Exception as e:
                        print(f"[GET PROFILE] Error decrypting referrer name: {e}")
                        referrer_name = "שם לא זמין"
                    
                    user_data['referred_by'] = {
                        'id': referrer.id,
                        'name': referrer_name,
                        'profile_image': get_cloudinary_url(referrer.profile_image)
                    }
        except Exception as e:
            print(f"[GET PROFILE] Error getting referrer info: {e}")
            # Continue without referrer info
        
        # Check if current user has liked this user
        try:
            match = Match.query.filter_by(
                user_id=current_user_id,
                liked_user_id=user_id
            ).first()
            user_data['liked_by_me'] = match is not None
            user_data['is_mutual'] = match.is_mutual if match else False
        except Exception as e:
            print(f"[GET PROFILE] Error checking match: {e}")
            user_data['liked_by_me'] = False
            user_data['is_mutual'] = False
        
        print(f"[GET PROFILE] ✅ Successfully prepared user data")
        print(f"[GET PROFILE] Returning user_data keys: {list(user_data.keys())}")
        print(f"[GET PROFILE] ========== END ==========")
        return jsonify({'user': user_data}), 200
        
    except Exception as e:
        print(f"[GET PROFILE] ❌❌❌ UNEXPECTED ERROR: {e}")
        import traceback
        print(f"[GET PROFILE] Full traceback:")
        traceback.print_exc()
        print(f"[GET PROFILE] ========== ERROR END ==========")
        return jsonify({'error': str(e)}), 500


@users_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    """Search users with filters"""
    try:
        current_user_id = get_current_user_id()
        
        # Get query parameters
        query = request.args.get('q', '')
        gender = request.args.get('gender')
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        location = request.args.get('location')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        users_query = User.query.filter(User.id != current_user_id)
        
        # Debug
        total_users = User.query.count()
        print(f"[SEARCH DEBUG] Total users in DB: {total_users}")
        print(f"[SEARCH DEBUG] Current user ID: {current_user_id}")
        print(f"[SEARCH DEBUG] Filters - gender: {gender}, min_age: {min_age}, max_age: {max_age}, location: {location}")
        
        # Apply filters
        if gender:
            users_query = users_query.filter(User.gender == gender)
        
        if min_age:
            users_query = users_query.filter(User.age >= min_age)
        
        if max_age:
            users_query = users_query.filter(User.age <= max_age)
        
        if location:
            users_query = users_query.filter(User.location.ilike(f'%{location}%'))
        
        # Pagination
        pagination = users_query.paginate(page=page, per_page=per_page, error_out=False)
        users = pagination.items
        
        print(f"[SEARCH DEBUG] Users found after filters: {len(users)}")
        print(f"[SEARCH DEBUG] Total matching users: {pagination.total}")
        
        # Prepare response
        users_data = []
        for user in users:
            user_dict = user.to_dict()
            user_dict['full_name'] = encryption_service.decrypt(user.full_name_encrypted)
            
            # Convert Cloudinary public_id to full URL
            user_dict['profile_image'] = get_cloudinary_url(user.profile_image)
            
            # Get referrer info
            referral = Referral.query.filter_by(referred_id=user.id).first()
            if referral:
                referrer = User.query.get(referral.referrer_id)
                if referrer:
                    user_dict['referred_by'] = {
                        'id': referrer.id,
                        'name': encryption_service.decrypt(referrer.full_name_encrypted)
                    }
            
            users_data.append(user_dict)
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/like/<int:user_id>', methods=['POST'])
@jwt_required()
def like_user(user_id):
    """Like/match with another user"""
    try:
        current_user_id = get_current_user_id()
        
        if current_user_id == user_id:
            return jsonify({'error': 'Cannot like yourself'}), 400
        
        # Check if user exists
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if already liked
        existing_match = Match.query.filter_by(
            user_id=current_user_id,
            liked_user_id=user_id
        ).first()
        
        if existing_match:
            return jsonify({'error': 'Already liked this user'}), 400
        
        # Create match
        new_match = Match(
            user_id=current_user_id,
            liked_user_id=user_id
        )
        
        # Check if mutual (the other user already liked this user)
        reverse_match = Match.query.filter_by(
            user_id=user_id,
            liked_user_id=current_user_id
        ).first()
        
        if reverse_match:
            new_match.is_mutual = True
            reverse_match.is_mutual = True
        
        db.session.add(new_match)
        db.session.commit()
        
        return jsonify({
            'message': 'User liked successfully',
            'is_mutual': new_match.is_mutual
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@users_bp.route('/matches', methods=['GET'])
@jwt_required()
def get_matches():
    """Get all mutual matches for current user"""
    try:
        current_user_id = get_current_user_id()
        
        # Get all mutual matches
        matches = Match.query.filter(
            and_(
                Match.user_id == current_user_id,
                Match.is_mutual == True
            )
        ).all()
        
        matches_data = []
        for match in matches:
            user = User.query.get(match.liked_user_id)
            if user:
                user_dict = user.to_dict()
                user_dict['full_name'] = encryption_service.decrypt(user.full_name_encrypted)
                user_dict['matched_at'] = match.created_at.isoformat()
                
                # Convert Cloudinary public_id to full URL
                user_dict['profile_image'] = get_cloudinary_url(user.profile_image)
                
                matches_data.append(user_dict)
        
        return jsonify({'matches': matches_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile"""
    try:
        current_user_id = get_current_user_id()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update public fields
        if 'age' in data:
            user.age = int(data['age']) if data['age'] and str(data['age']).strip() else None
        if 'gender' in data:
            user.gender = data['gender'] if data['gender'] else None
        if 'location' in data:
            user.location = data['location'].strip() if data['location'] and data['location'].strip() else None
        if 'height' in data:
            user.height = int(data['height']) if data['height'] and str(data['height']).strip() else None
        if 'employment_status' in data:
            user.employment_status = data['employment_status'].strip() if data['employment_status'] and data['employment_status'].strip() else None
        if 'social_link' in data:
            social_link_value = data['social_link'].strip() if data['social_link'] and data['social_link'].strip() else None
            user.social_link = social_link_value
            print(f"[UPDATE PROFILE] Setting social_link to: {social_link_value}")  # Debug log
        if 'interests' in data:
            user.interests = data['interests'] if data['interests'] else None
        if 'bio' in data:
            user.bio = data['bio'] if data['bio'] else None
        if 'profile_image' in data:
            user.profile_image = data['profile_image'] if data['profile_image'] else None
        
        # Update encrypted fields
        if 'phone' in data:
            user.phone_encrypted = encryption_service.encrypt(data['phone']) if data['phone'] else None
        if 'address' in data:
            user.address_encrypted = encryption_service.encrypt(data['address']) if data['address'] else None
        
        db.session.commit()
        print(f"[UPDATE PROFILE] After commit, user.social_link = {user.social_link}")  # Debug log
        
        # Return updated user data
        user_data = user.to_dict()
        user_data['email'] = encryption_service.decrypt(user.email_encrypted)
        user_data['full_name'] = encryption_service.decrypt(user.full_name_encrypted)
        user_data['phone'] = encryption_service.decrypt(user.phone_encrypted) if user.phone_encrypted else None
        user_data['address'] = encryption_service.decrypt(user.address_encrypted) if user.address_encrypted else None
        
        print(f"[UPDATE PROFILE] Returning user_data with social_link: {user_data.get('social_link')}")  # Debug log
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

