from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Match, Referral
from encryption import encryption_service
from sqlalchemy import or_, and_

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/profile/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    """Get user profile by ID"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Basic user data
        user_data = user.to_dict()
        user_data['full_name'] = encryption_service.decrypt(user.full_name_encrypted)
        
        # Get referrer info
        referral = Referral.query.filter_by(referred_id=user.id).first()
        if referral:
            referrer = User.query.get(referral.referrer_id)
            if referrer:
                user_data['referred_by'] = {
                    'id': referrer.id,
                    'name': encryption_service.decrypt(referrer.full_name_encrypted),
                    'profile_image': referrer.profile_image
                }
        
        # Check if current user has liked this user
        match = Match.query.filter_by(
            user_id=current_user_id,
            liked_user_id=user_id
        ).first()
        user_data['liked_by_me'] = match is not None
        user_data['is_mutual'] = match.is_mutual if match else False
        
        return jsonify({'user': user_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    """Search users with filters"""
    try:
        current_user_id = get_jwt_identity()
        
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
        
        # Prepare response
        users_data = []
        for user in users:
            user_dict = user.to_dict()
            user_dict['full_name'] = encryption_service.decrypt(user.full_name_encrypted)
            
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
        current_user_id = get_jwt_identity()
        
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
        current_user_id = get_jwt_identity()
        
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
                matches_data.append(user_dict)
        
        return jsonify({'matches': matches_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update public fields
        if 'age' in data:
            user.age = data['age']
        if 'gender' in data:
            user.gender = data['gender']
        if 'location' in data:
            user.location = data['location']
        if 'interests' in data:
            user.interests = data['interests']
        if 'bio' in data:
            user.bio = data['bio']
        if 'profile_image' in data:
            user.profile_image = data['profile_image']
        
        # Update encrypted fields
        if 'phone' in data:
            user.phone_encrypted = encryption_service.encrypt(data['phone']) if data['phone'] else None
        if 'address' in data:
            user.address_encrypted = encryption_service.encrypt(data['address']) if data['address'] else None
        
        db.session.commit()
        
        # Return updated user data
        user_data = user.to_dict()
        user_data['email'] = encryption_service.decrypt(user.email_encrypted)
        user_data['full_name'] = encryption_service.decrypt(user.full_name_encrypted)
        user_data['phone'] = encryption_service.decrypt(user.phone_encrypted) if user.phone_encrypted else None
        user_data['address'] = encryption_service.decrypt(user.address_encrypted) if user.address_encrypted else None
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

