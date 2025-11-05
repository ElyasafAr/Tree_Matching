from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, User, Referral
from encryption import encryption_service
from utils import get_current_user_id
import cloudinary
import os

referrals_bp = Blueprint('referrals', __name__, url_prefix='/referrals')

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
    if public_id.startswith('http'):
        return public_id
    return cloudinary.CloudinaryImage(public_id).build_url(
        secure=True,
        transformation=[
            {'quality': 'auto:good'},
            {'fetch_format': 'auto'}
        ]
    )

@referrals_bp.route('/my-referrals', methods=['GET'])
@jwt_required()
def get_my_referrals():
    """Get all users that current user has referred"""
    try:
        current_user_id = get_current_user_id()
        
        # Get all referrals made by this user
        referrals = Referral.query.filter_by(referrer_id=current_user_id).all()
        
        referrals_data = []
        for referral in referrals:
            user = User.query.get(referral.referred_id)
            if user:
                user_dict = {
                    'id': user.id,
                    'name': encryption_service.decrypt(user.full_name_encrypted),
                    'profile_image': get_cloudinary_url(user.profile_image),
                    'age': user.age,
                    'gender': user.gender,
                    'location': user.location,
                    'referred_at': referral.created_at.isoformat()
                }
                referrals_data.append(user_dict)
        
        return jsonify({'referrals': referrals_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@referrals_bp.route('/tree', methods=['GET'])
@jwt_required()
def get_referral_tree():
    """Get referral tree starting from current user"""
    try:
        current_user_id = get_current_user_id()
        
        def build_tree(user_id, depth=0, max_depth=3):
            """Recursively build referral tree"""
            if depth >= max_depth:
                return None
            
            user = User.query.get(user_id)
            if not user:
                return None
            
            # Get direct referrals
            referrals = Referral.query.filter_by(referrer_id=user_id).all()
            
            children = []
            for referral in referrals:
                child_tree = build_tree(referral.referred_id, depth + 1, max_depth)
                if child_tree:
                    children.append(child_tree)
            
            return {
                'id': user.id,
                'name': encryption_service.decrypt(user.full_name_encrypted),
                'profile_image': get_cloudinary_url(user.profile_image),
                'referral_code': user.referral_code,
                'children': children,
                'children_count': len(referrals)
            }
        
        tree = build_tree(current_user_id)
        
        return jsonify({'tree': tree}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@referrals_bp.route('/my-referrer', methods=['GET'])
@jwt_required()
def get_my_referrer():
    """Get the user who referred the current user"""
    try:
        current_user_id = get_current_user_id()
        
        # Find referral record
        referral = Referral.query.filter_by(referred_id=current_user_id).first()
        
        if not referral:
            return jsonify({'referrer': None}), 200
        
        referrer = User.query.get(referral.referrer_id)
        if not referrer:
            return jsonify({'referrer': None}), 200
        
        referrer_data = {
            'id': referrer.id,
            'name': encryption_service.decrypt(referrer.full_name_encrypted),
            'profile_image': get_cloudinary_url(referrer.profile_image),
            'age': referrer.age,
            'gender': referrer.gender,
            'location': referrer.location,
            'bio': referrer.bio,
            'referral_code': referrer.referral_code
        }
        
        return jsonify({'referrer': referrer_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@referrals_bp.route('/chain/<int:user_id>', methods=['GET'])
@jwt_required()
def get_referral_chain(user_id):
    """Get the referral chain from a user back to the root"""
    try:
        current_user_id = get_current_user_id()
        
        def build_chain(uid, chain=None, max_depth=10):
            """Build chain of referrers going backwards"""
            if chain is None:
                chain = []
            
            if len(chain) >= max_depth:
                return chain
            
            user = User.query.get(uid)
            if not user:
                return chain
            
            chain.append({
                'id': user.id,
                'name': encryption_service.decrypt(user.full_name_encrypted),
                'profile_image': get_cloudinary_url(user.profile_image)
            })
            
            # Find who referred this user
            referral = Referral.query.filter_by(referred_id=uid).first()
            if referral:
                return build_chain(referral.referrer_id, chain, max_depth)
            
            return chain
        
        chain = build_chain(user_id)
        
        # Calculate connection distance to current user
        current_chain = build_chain(current_user_id)
        
        # Find common ancestor
        connection_distance = None
        for i, user1 in enumerate(chain):
            for j, user2 in enumerate(current_chain):
                if user1['id'] == user2['id']:
                    connection_distance = i + j
                    break
            if connection_distance is not None:
                break
        
        return jsonify({
            'chain': chain,
            'connection_distance': connection_distance
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@referrals_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_referral_stats():
    """Get referral statistics for current user"""
    try:
        current_user_id = get_current_user_id()
        
        # Count direct referrals
        direct_count = Referral.query.filter_by(referrer_id=current_user_id).count()
        
        # Count total referrals in tree (recursive)
        def count_tree_referrals(user_id, counted=None):
            if counted is None:
                counted = set()
            
            if user_id in counted:
                return 0
            
            counted.add(user_id)
            referrals = Referral.query.filter_by(referrer_id=user_id).all()
            
            total = len(referrals)
            for referral in referrals:
                total += count_tree_referrals(referral.referred_id, counted)
            
            return total
        
        total_count = count_tree_referrals(current_user_id)
        
        return jsonify({
            'direct_referrals': direct_count,
            'total_referrals': total_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

