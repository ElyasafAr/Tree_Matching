from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, User, Match, Referral, Chat, Message, Block
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
        
        # Check if current user has blocked this user
        try:
            block = Block.query.filter_by(
                blocker_id=current_user_id,
                blocked_id=user_id
            ).first()
            user_data['blocked_by_me'] = block is not None
        except Exception as e:
            print(f"[GET PROFILE] Error checking block: {e}")
            user_data['blocked_by_me'] = False
        
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
        query = request.args.get('q', '').strip()
        name_search = request.args.get('name', '').strip()
        gender = request.args.get('gender')
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        location = request.args.get('location')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query - exclude suspended users and blocked users
        users_query = User.query.filter(User.id != current_user_id).filter(User.is_suspended == False)
        
        # Get list of blocked user IDs (both ways - users I blocked and users who blocked me)
        blocked_by_me = [b.blocked_id for b in Block.query.filter_by(blocker_id=current_user_id).all()]
        blocked_me = [b.blocker_id for b in Block.query.filter_by(blocked_id=current_user_id).all()]
        all_blocked_ids = set(blocked_by_me + blocked_me)
        
        # Exclude blocked users
        if all_blocked_ids:
            users_query = users_query.filter(~User.id.in_(all_blocked_ids))
        
        # Debug
        total_users = User.query.count()
        print(f"[SEARCH DEBUG] Total users in DB: {total_users}")
        print(f"[SEARCH DEBUG] Current user ID: {current_user_id}")
        print(f"[SEARCH DEBUG] Filters - name: '{name_search}', gender: {gender}, min_age: {min_age}, max_age: {max_age}, location: {location}")
        
        # Filter by name if provided (requires decryption - must be done before other filters)
        if name_search:
            name_search_lower = name_search.lower().strip()
            print(f"[SEARCH DEBUG] Searching for name: '{name_search_lower}'")
            
            # Get all users that match basic criteria (not suspended, not blocked, not current user)
            base_query = User.query.filter(User.id != current_user_id).filter(User.is_suspended == False)
            
            # Exclude blocked users
            if all_blocked_ids:
                base_query = base_query.filter(~User.id.in_(all_blocked_ids))
            
            all_candidates = base_query.all()
            print(f"[SEARCH DEBUG] Found {len(all_candidates)} candidate users before name filter")
            
            # Filter by name (decrypt and check)
            filtered_users = []
            for user in all_candidates:
                try:
                    full_name = encryption_service.decrypt(user.full_name_encrypted)
                    full_name_lower = full_name.lower()
                    if name_search_lower in full_name_lower:
                        filtered_users.append(user)
                        print(f"[SEARCH DEBUG] Match found: user {user.id} - '{full_name}' contains '{name_search_lower}'")
                except Exception as e:
                    print(f"[SEARCH DEBUG] Error decrypting name for user {user.id}: {e}")
                    # Skip users with decryption errors
            print(f"[SEARCH DEBUG] After name filter: {len(filtered_users)} users match")
            all_users = filtered_users
            
            # Now apply other filters on the name-filtered results
            if gender:
                all_users = [u for u in all_users if u.gender == gender]
            if min_age:
                all_users = [u for u in all_users if u.age and u.age >= min_age]
            if max_age:
                all_users = [u for u in all_users if u.age and u.age <= max_age]
            if location:
                location_lower = location.lower()
                all_users = [u for u in all_users if u.location and location_lower in u.location.lower()]
        else:
            # No name search - apply filters normally using SQL query
            if gender:
                users_query = users_query.filter(User.gender == gender)
            
            if min_age:
                users_query = users_query.filter(User.age >= min_age)
            
            if max_age:
                users_query = users_query.filter(User.age <= max_age)
            
            if location:
                users_query = users_query.filter(User.location.ilike(f'%{location}%'))
            
            all_users = users_query.all()
        
        # Pagination (manual since we filtered by name)
        total_filtered = len(all_users)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        users = all_users[start_idx:end_idx]
        
        print(f"[SEARCH DEBUG] Users found after filters: {len(users)}")
        print(f"[SEARCH DEBUG] Total matching users: {total_filtered}")
        
        # Calculate total pages
        total_pages = (total_filtered + per_page - 1) // per_page if total_filtered > 0 else 1
        
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
                'total': total_filtered,
                'pages': total_pages
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


@users_bp.route('/test-social-link/<int:user_id>', methods=['GET'])
@jwt_required()
def test_social_link(user_id):
    """Test endpoint to check social_link retrieval"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Direct DB query
        from sqlalchemy import text
        result = db.session.execute(text("SELECT social_link FROM users WHERE id = :user_id"), {"user_id": user_id})
        db_row = result.fetchone()
        db_value = db_row[0] if db_row else None
        
        # Get from model
        model_value = user.social_link
        
        # Get from to_dict
        user_dict = user.to_dict()
        dict_value = user_dict.get('social_link')
        
        return jsonify({
            'user_id': user_id,
            'direct_db_query': db_value,
            'model_attribute': model_value,
            'to_dict_value': dict_value,
            'to_dict_keys': list(user_dict.keys()),
            'to_dict_full': user_dict
        }), 200
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
        print(f"[UPDATE PROFILE] ========== START ==========")
        print(f"[UPDATE PROFILE] Received data keys: {list(data.keys())}")
        print(f"[UPDATE PROFILE] social_link in data: {'social_link' in data}")
        if 'social_link' in data:
            print(f"[UPDATE PROFILE] social_link value: '{data['social_link']}'")
            print(f"[UPDATE PROFILE] social_link type: {type(data['social_link'])}")
            print(f"[UPDATE PROFILE] social_link is None: {data['social_link'] is None}")
            print(f"[UPDATE PROFILE] social_link bool: {bool(data['social_link'])}")
        
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
        if 'religious_status' in data:
            user.religious_status = data['religious_status'].strip() if data['religious_status'] and data['religious_status'].strip() else None
        if 'social_link' in data:
            # Handle social_link - allow empty strings to be saved as None
            social_link_raw = data['social_link']
            print(f"[UPDATE PROFILE] social_link_raw: '{social_link_raw}' (type: {type(social_link_raw)})")
            
            if social_link_raw is None:
                social_link_value = None
            elif isinstance(social_link_raw, str):
                social_link_value = social_link_raw.strip() if social_link_raw.strip() else None
            else:
                social_link_value = str(social_link_raw).strip() if str(social_link_raw).strip() else None
            
            print(f"[UPDATE PROFILE] Setting social_link to: '{social_link_value}' (type: {type(social_link_value)})")
            user.social_link = social_link_value
            print(f"[UPDATE PROFILE] user.social_link after assignment: '{user.social_link}'")
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
        
        print(f"[UPDATE PROFILE] Before commit, user.social_link = '{user.social_link}'")
        db.session.commit()
        print(f"[UPDATE PROFILE] After commit, user.social_link = '{user.social_link}'")
        
        # Verify directly from database
        from sqlalchemy import text
        result = db.session.execute(text("SELECT social_link FROM users WHERE id = :user_id"), {"user_id": current_user_id})
        db_value = result.fetchone()
        print(f"[UPDATE PROFILE] Direct DB query result: '{db_value[0] if db_value and db_value[0] else 'NULL/EMPTY'}'")
        
        # Refresh user from database to verify
        db.session.refresh(user)
        print(f"[UPDATE PROFILE] After refresh, user.social_link = '{user.social_link}'")
        
        # Query user again to ensure we have the latest data
        user = User.query.get(current_user_id)
        print(f"[UPDATE PROFILE] After re-query, user.social_link = '{user.social_link}'")
        
        # Return updated user data
        user_data = user.to_dict()
        print(f"[UPDATE PROFILE] user_data from to_dict() keys: {list(user_data.keys())}")
        print(f"[UPDATE PROFILE] user_data['social_link'] = '{user_data.get('social_link')}'")
        print(f"[UPDATE PROFILE] user_data['social_link'] type: {type(user_data.get('social_link'))}")
        print(f"[UPDATE PROFILE] user_data['social_link'] is None: {user_data.get('social_link') is None}")
        print(f"[UPDATE PROFILE] 'social_link' in user_data: {'social_link' in user_data}")
        
        user_data['email'] = encryption_service.decrypt(user.email_encrypted)
        user_data['full_name'] = encryption_service.decrypt(user.full_name_encrypted)
        user_data['phone'] = encryption_service.decrypt(user.phone_encrypted) if user.phone_encrypted else None
        user_data['address'] = encryption_service.decrypt(user.address_encrypted) if user.address_encrypted else None
        
        # Ensure social_link is explicitly included even if None
        if 'social_link' not in user_data:
            user_data['social_link'] = user.social_link
            print(f"[UPDATE PROFILE] Added social_link explicitly: '{user_data.get('social_link')}'")
        
        print(f"[UPDATE PROFILE] Returning user_data with social_link: {user_data.get('social_link')}")  # Debug log
        print(f"[UPDATE PROFILE] Full user_data before jsonify: {user_data}")
        print(f"[UPDATE PROFILE] 'social_link' in user_data: {'social_link' in user_data}")
        
        response_data = {
            'message': 'Profile updated successfully',
            'user': user_data
        }
        print(f"[UPDATE PROFILE] Response data before jsonify: {response_data}")
        print(f"[UPDATE PROFILE] 'social_link' in response_data['user']: {'social_link' in response_data['user']}")
        
        # Test jsonify
        import json
        json_str = json.dumps(response_data, default=str)
        print(f"[UPDATE PROFILE] JSON string: {json_str[:500]}...")  # First 500 chars
        json_parsed = json.loads(json_str)
        print(f"[UPDATE PROFILE] Parsed JSON 'social_link' in user: {'social_link' in json_parsed.get('user', {})}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@users_bp.route('/is-admin', methods=['GET'])
@jwt_required()
def check_is_admin():
    """Check if current user is the root/admin (has no referrer)"""
    try:
        current_user_id = get_current_user_id()
        
        # Check if user has a referrer - if not, they are the root/admin
        referral = Referral.query.filter_by(referred_id=current_user_id).first()
        is_admin = referral is None
        
        return jsonify({'is_admin': is_admin}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    """Get admin statistics - only accessible to root user"""
    try:
        current_user_id = get_current_user_id()
        
        # Verify user is admin (root)
        referral = Referral.query.filter_by(referred_id=current_user_id).first()
        if referral:
            return jsonify({'error': 'Unauthorized - Admin access only'}), 403
        
        # Get statistics
        total_users = User.query.count()
        total_referrals = Referral.query.count()
        total_matches = Match.query.count()
        total_mutual_matches = Match.query.filter_by(is_mutual=True).count()
        total_chats = Chat.query.count()
        total_messages = Message.query.count()
        
        # Get users by gender
        from sqlalchemy import func
        gender_stats = db.session.query(
            User.gender,
            func.count(User.id).label('count')
        ).group_by(User.gender).all()
        
        gender_breakdown = {gender or 'לא מוגדר': count for gender, count in gender_stats}
        
        # Get recent users (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_users = User.query.filter(User.created_at >= week_ago).count()
        
        # Get active users (logged in last 7 days)
        active_users = User.query.filter(User.last_active >= week_ago).count()
        
        return jsonify({
            'total_users': total_users,
            'total_referrals': total_referrals,
            'total_matches': total_matches,
            'total_mutual_matches': total_mutual_matches,
            'total_chats': total_chats,
            'total_messages': total_messages,
            'gender_breakdown': gender_breakdown,
            'recent_users': recent_users,
            'active_users': active_users
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users for admin - only accessible to root user"""
    try:
        current_user_id = get_current_user_id()
        
        # Verify user is admin (root)
        referral = Referral.query.filter_by(referred_id=current_user_id).first()
        if referral:
            return jsonify({'error': 'Unauthorized - Admin access only'}), 403
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search_name = request.args.get('name', '').strip()
        
        # Build query
        users_query = User.query
        
        # Filter by name if provided
        if search_name:
            search_name_lower = search_name.lower()
            all_users = users_query.all()
            filtered_users = []
            for user in all_users:
                try:
                    full_name = encryption_service.decrypt(user.full_name_encrypted)
                    if search_name_lower in full_name.lower():
                        filtered_users.append(user)
                except Exception as e:
                    print(f"[ADMIN USERS] Error decrypting name for user {user.id}: {e}")
            users_query = User.query.filter(User.id.in_([u.id for u in filtered_users]))
        
        # Pagination
        pagination = users_query.paginate(page=page, per_page=per_page, error_out=False)
        users = pagination.items
        
        # Prepare response
        users_data = []
        for user in users:
            try:
                user_dict = user.to_dict()
                user_dict['full_name'] = encryption_service.decrypt(user.full_name_encrypted)
                user_dict['email'] = encryption_service.decrypt(user.email_encrypted)
                user_dict['is_suspended'] = user.is_suspended
                
                # Convert Cloudinary public_id to full URL
                user_dict['profile_image'] = get_cloudinary_url(user.profile_image)
                
                # Get referral count
                referral_count = Referral.query.filter_by(referrer_id=user.id).count()
                user_dict['referrals_count'] = referral_count
                
                # Check if user is root/admin
                has_referrer = Referral.query.filter_by(referred_id=user.id).first() is not None
                user_dict['is_root'] = not has_referrer
                
                users_data.append(user_dict)
            except Exception as e:
                print(f"[ADMIN USERS] Error processing user {user.id}: {e}")
                continue
        
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


@users_bp.route('/admin/users/<int:user_id>/suspend', methods=['POST'])
@jwt_required()
def suspend_user(user_id):
    """Suspend a user - only accessible to root user"""
    try:
        current_user_id = get_current_user_id()
        
        # Verify user is admin (root)
        referral = Referral.query.filter_by(referred_id=current_user_id).first()
        if referral:
            return jsonify({'error': 'Unauthorized - Admin access only'}), 403
        
        # Cannot suspend yourself
        if current_user_id == user_id:
            return jsonify({'error': 'Cannot suspend yourself'}), 400
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user is root (cannot suspend root)
        has_referrer = Referral.query.filter_by(referred_id=user_id).first() is not None
        if not has_referrer:
            return jsonify({'error': 'Cannot suspend root user'}), 400
        
        # Suspend user
        user.is_suspended = True
        db.session.commit()
        
        return jsonify({
            'message': 'User suspended successfully',
            'user_id': user_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@users_bp.route('/admin/users/<int:user_id>/unsuspend', methods=['POST'])
@jwt_required()
def unsuspend_user(user_id):
    """Unsuspend a user - only accessible to root user"""
    try:
        current_user_id = get_current_user_id()
        
        # Verify user is admin (root)
        referral = Referral.query.filter_by(referred_id=current_user_id).first()
        if referral:
            return jsonify({'error': 'Unauthorized - Admin access only'}), 403
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Unsuspend user
        user.is_suspended = False
        db.session.commit()
        
        return jsonify({
            'message': 'User unsuspended successfully',
            'user_id': user_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@users_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user - only accessible to root user"""
    try:
        current_user_id = get_current_user_id()
        
        # Verify user is admin (root)
        referral = Referral.query.filter_by(referred_id=current_user_id).first()
        if referral:
            return jsonify({'error': 'Unauthorized - Admin access only'}), 403
        
        # Cannot delete yourself
        if current_user_id == user_id:
            return jsonify({'error': 'Cannot delete yourself'}), 400
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user is root (cannot delete root)
        has_referrer = Referral.query.filter_by(referred_id=user_id).first() is not None
        if not has_referrer:
            return jsonify({'error': 'Cannot delete root user'}), 400
        
        # Delete related data first
        # Delete messages
        Message.query.filter_by(sender_id=user_id).delete()
        # Delete chats
        Chat.query.filter((Chat.user1_id == user_id) | (Chat.user2_id == user_id)).delete()
        # Delete matches
        Match.query.filter((Match.user_id == user_id) | (Match.liked_user_id == user_id)).delete()
        # Delete referrals (both as referrer and referred)
        Referral.query.filter((Referral.referrer_id == user_id) | (Referral.referred_id == user_id)).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User deleted successfully',
            'user_id': user_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@users_bp.route('/block/<int:user_id>', methods=['POST'])
@jwt_required()
def block_user(user_id):
    """Block a user (unlike/block)"""
    try:
        current_user_id = get_current_user_id()
        
        if current_user_id == user_id:
            return jsonify({'error': 'Cannot block yourself'}), 400
        
        # Check if user exists
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if already blocked
        existing_block = Block.query.filter_by(
            blocker_id=current_user_id,
            blocked_id=user_id
        ).first()
        
        if existing_block:
            return jsonify({'error': 'User already blocked'}), 400
        
        # Remove match if exists (unlike)
        match = Match.query.filter_by(
            user_id=current_user_id,
            liked_user_id=user_id
        ).first()
        
        if match:
            # If mutual, also remove the mutual flag from reverse match
            if match.is_mutual:
                reverse_match = Match.query.filter_by(
                    user_id=user_id,
                    liked_user_id=current_user_id
                ).first()
                if reverse_match:
                    reverse_match.is_mutual = False
            
            db.session.delete(match)
        
        # Create block
        new_block = Block(
            blocker_id=current_user_id,
            blocked_id=user_id
        )
        
        db.session.add(new_block)
        db.session.commit()
        
        return jsonify({
            'message': 'User blocked successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@users_bp.route('/unblock/<int:user_id>', methods=['POST'])
@jwt_required()
def unblock_user(user_id):
    """Unblock a user"""
    try:
        current_user_id = get_current_user_id()
        
        # Check if block exists
        block = Block.query.filter_by(
            blocker_id=current_user_id,
            blocked_id=user_id
        ).first()
        
        if not block:
            return jsonify({'error': 'User is not blocked'}), 404
        
        # Remove block
        db.session.delete(block)
        db.session.commit()
        
        return jsonify({
            'message': 'User unblocked successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@users_bp.route('/blocked', methods=['GET'])
@jwt_required()
def get_blocked_users():
    """Get all users blocked by current user"""
    try:
        current_user_id = get_current_user_id()
        
        # Get all blocks
        blocks = Block.query.filter_by(blocker_id=current_user_id).all()
        
        blocked_users = []
        for block in blocks:
            user = User.query.get(block.blocked_id)
            if user and not user.is_suspended:
                try:
                    user_dict = user.to_dict()
                    user_dict['full_name'] = encryption_service.decrypt(user.full_name_encrypted)
                    user_dict['profile_image'] = get_cloudinary_url(user.profile_image)
                    user_dict['blocked_at'] = block.created_at.isoformat() if block.created_at else None
                    blocked_users.append(user_dict)
                except Exception as e:
                    print(f"[GET BLOCKED] Error processing user {user.id}: {e}")
                    continue
        
        return jsonify({'blocked_users': blocked_users}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

