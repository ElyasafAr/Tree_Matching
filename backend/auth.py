import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, Referral
from encryption import encryption_service

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with a referral code"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'full_name', 'referral_code']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if referral code exists
        referrer = User.query.filter_by(referral_code=data['referral_code']).first()
        if not referrer:
            return jsonify({'error': 'Invalid referral code'}), 400
        
        # Check if email already exists (need to check encrypted emails)
        email_to_check = encryption_service.encrypt(data['email'].lower().strip())
        existing_user = User.query.filter_by(email_encrypted=email_to_check).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Encrypt sensitive fields
        email_encrypted = encryption_service.encrypt(data['email'].lower().strip())
        full_name_encrypted = encryption_service.encrypt(data['full_name'])
        phone_encrypted = encryption_service.encrypt(data.get('phone', '')) if data.get('phone') else None
        address_encrypted = encryption_service.encrypt(data.get('address', '')) if data.get('address') else None
        
        # Create new user
        new_user = User(
            email_encrypted=email_encrypted,
            full_name_encrypted=full_name_encrypted,
            phone_encrypted=phone_encrypted,
            address_encrypted=address_encrypted,
            password_hash=password_hash,
            age=data.get('age'),
            gender=data.get('gender'),
            location=data.get('location'),
            interests=data.get('interests'),
            bio=data.get('bio'),
            profile_image=data.get('profile_image')
        )
        
        db.session.add(new_user)
        db.session.flush()  # Get the new_user.id
        
        # Create referral record
        referral = Referral(
            referrer_id=referrer.id,
            referred_id=new_user.id,
            referral_code_used=data['referral_code']
        )
        
        db.session.add(referral)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=new_user.id)
        
        # Prepare user data with decrypted fields
        user_data = new_user.to_dict()
        user_data['email'] = encryption_service.decrypt(new_user.email_encrypted)
        user_data['full_name'] = encryption_service.decrypt(new_user.full_name_encrypted)
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with email and password"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Encrypt email to search in database
        email_encrypted = encryption_service.encrypt(data['email'].lower().strip())
        
        # Find user
        user = User.query.filter_by(email_encrypted=email_encrypted).first()
        
        if not user:
            print(f"[LOGIN DEBUG] User not found for email: {data['email']}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        print(f"[LOGIN DEBUG] User found: ID={user.id}")
        
        # Verify password
        password_match = bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8'))
        print(f"[LOGIN DEBUG] Password match: {password_match}")
        
        if not password_match:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        # Prepare user data with decrypted fields
        user_data = user.to_dict()
        user_data['email'] = encryption_service.decrypt(user.email_encrypted)
        user_data['full_name'] = encryption_service.decrypt(user.full_name_encrypted)
        
        # Get referrer info
        referral = Referral.query.filter_by(referred_id=user.id).first()
        if referral:
            referrer = User.query.get(referral.referrer_id)
            if referrer:
                user_data['referred_by'] = {
                    'id': referrer.id,
                    'name': encryption_service.decrypt(referrer.full_name_encrypted)
                }
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current logged-in user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prepare user data with decrypted fields
        user_data = user.to_dict()
        user_data['email'] = encryption_service.decrypt(user.email_encrypted)
        user_data['full_name'] = encryption_service.decrypt(user.full_name_encrypted)
        user_data['phone'] = encryption_service.decrypt(user.phone_encrypted) if user.phone_encrypted else None
        user_data['address'] = encryption_service.decrypt(user.address_encrypted) if user.address_encrypted else None
        
        # Get referrer info
        referral = Referral.query.filter_by(referred_id=user.id).first()
        if referral:
            referrer = User.query.get(referral.referrer_id)
            if referrer:
                user_data['referred_by'] = {
                    'id': referrer.id,
                    'name': encryption_service.decrypt(referrer.full_name_encrypted)
                }
        
        return jsonify({'user': user_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/validate-referral/<code>', methods=['GET'])
def validate_referral_code(code):
    """Validate if a referral code exists"""
    try:
        user = User.query.filter_by(referral_code=code).first()
        
        if user:
            return jsonify({
                'valid': True,
                'referrer_name': encryption_service.decrypt(user.full_name_encrypted)
            }), 200
        else:
            return jsonify({'valid': False}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

