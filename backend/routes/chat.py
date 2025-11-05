from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, User, Chat, Message
from encryption import encryption_service
from utils import get_current_user_id
from datetime import datetime
import cloudinary
import os

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

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

@chat_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """Get all conversations for current user"""
    try:
        current_user_id = get_current_user_id()
        
        # Find all chats where user is participant
        chats = Chat.query.filter(
            (Chat.user1_id == current_user_id) | (Chat.user2_id == current_user_id)
        ).order_by(Chat.last_message_at.desc()).all()
        
        conversations = []
        for chat in chats:
            chat_dict = chat.to_dict(current_user_id)
            
            # Get other user info
            other_user_id = chat_dict['other_user_id']
            other_user = User.query.get(other_user_id)
            if other_user:
                chat_dict['other_user'] = {
                    'id': other_user.id,
                    'name': encryption_service.decrypt(other_user.full_name_encrypted),
                    'profile_image': get_cloudinary_url(other_user.profile_image)
                }
            
            conversations.append(chat_dict)
        
        return jsonify({'conversations': conversations}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/messages/<int:chat_id>', methods=['GET'])
@jwt_required()
def get_messages(chat_id):
    """Get all messages in a chat"""
    try:
        current_user_id = get_current_user_id()
        
        # Verify user is part of this chat
        chat = Chat.query.get(chat_id)
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        if chat.user1_id != current_user_id and chat.user2_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get messages with pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        pagination = Message.query.filter_by(chat_id=chat_id).order_by(
            Message.sent_at.asc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        messages = [msg.to_dict() for msg in pagination.items]
        
        # Mark messages as read
        Message.query.filter(
            Message.chat_id == chat_id,
            Message.sender_id != current_user_id,
            Message.is_read == False
        ).update({'is_read': True})
        db.session.commit()
        
        return jsonify({
            'messages': messages,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    """Send a message to another user"""
    try:
        current_user_id = get_current_user_id()
        data = request.get_json()
        
        if not data.get('recipient_id') or not data.get('content'):
            return jsonify({'error': 'recipient_id and content are required'}), 400
        
        recipient_id = data['recipient_id']
        
        # Check if recipient exists
        recipient = User.query.get(recipient_id)
        if not recipient:
            return jsonify({'error': 'Recipient not found'}), 404
        
        # Find or create chat
        chat = Chat.query.filter(
            ((Chat.user1_id == current_user_id) & (Chat.user2_id == recipient_id)) |
            ((Chat.user1_id == recipient_id) & (Chat.user2_id == current_user_id))
        ).first()
        
        if not chat:
            # Create new chat (ensure user1_id < user2_id for consistency)
            user1_id = min(current_user_id, recipient_id)
            user2_id = max(current_user_id, recipient_id)
            
            chat = Chat(
                user1_id=user1_id,
                user2_id=user2_id
            )
            db.session.add(chat)
            db.session.flush()
        
        # Create message
        message = Message(
            chat_id=chat.id,
            sender_id=current_user_id,
            content=data['content']
        )
        
        # Update chat's last_message_at
        chat.last_message_at = datetime.utcnow()
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'message': 'Message sent successfully',
            'data': message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/start/<int:user_id>', methods=['POST'])
@jwt_required()
def start_chat(user_id):
    """Start a chat with another user (or get existing chat)"""
    try:
        current_user_id = get_current_user_id()
        
        if current_user_id == user_id:
            return jsonify({'error': 'Cannot chat with yourself'}), 400
        
        # Check if user exists
        other_user = User.query.get(user_id)
        if not other_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Find existing chat
        chat = Chat.query.filter(
            ((Chat.user1_id == current_user_id) & (Chat.user2_id == user_id)) |
            ((Chat.user1_id == user_id) & (Chat.user2_id == current_user_id))
        ).first()
        
        if not chat:
            # Create new chat
            user1_id = min(current_user_id, user_id)
            user2_id = max(current_user_id, user_id)
            
            chat = Chat(
                user1_id=user1_id,
                user2_id=user2_id
            )
            db.session.add(chat)
            db.session.commit()
        
        chat_dict = chat.to_dict(current_user_id)
        chat_dict['other_user'] = {
            'id': other_user.id,
            'name': encryption_service.decrypt(other_user.full_name_encrypted),
            'profile_image': get_cloudinary_url(other_user.profile_image)
        }
        
        return jsonify({'chat': chat_dict}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get count of unread messages for current user"""
    try:
        current_user_id = get_current_user_id()
        
        # Get all chats where user is participant
        chats = Chat.query.filter(
            (Chat.user1_id == current_user_id) | (Chat.user2_id == current_user_id)
        ).all()
        
        chat_ids = [chat.id for chat in chats]
        
        # Count unread messages
        unread_count = Message.query.filter(
            Message.chat_id.in_(chat_ids),
            Message.sender_id != current_user_id,
            Message.is_read == False
        ).count()
        
        return jsonify({'unread_count': unread_count}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/delete/<int:chat_id>', methods=['DELETE'])
@jwt_required()
def delete_chat(chat_id):
    """Delete a chat conversation and all its messages"""
    try:
        current_user_id = get_current_user_id()
        
        # Get the chat
        chat = Chat.query.get(chat_id)
        
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        # Check if user is part of this chat
        if chat.user1_id != current_user_id and chat.user2_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Delete all messages in this chat
        Message.query.filter_by(chat_id=chat_id).delete()
        
        # Delete the chat
        db.session.delete(chat)
        db.session.commit()
        
        return jsonify({'message': 'Chat deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

