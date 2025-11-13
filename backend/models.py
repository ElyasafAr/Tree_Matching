from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets

db = SQLAlchemy()

class User(db.Model):
    """User model - stores user information with encrypted sensitive fields"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Email hash for lookups (deterministic)
    email_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    
    # Encrypted fields (for secure storage)
    email_encrypted = db.Column(db.Text, nullable=False)
    full_name_encrypted = db.Column(db.Text, nullable=False)
    phone_encrypted = db.Column(db.Text, nullable=True)
    address_encrypted = db.Column(db.Text, nullable=True)
    
    # Hashed password (not encrypted, uses bcrypt)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Public fields
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)  # male, female, other
    location = db.Column(db.String(100), nullable=True)  # City/Region
    height = db.Column(db.Integer, nullable=True)  # Height in cm
    employment_status = db.Column(db.String(100), nullable=True)  # Employment status
    interests = db.Column(db.Text, nullable=True)  # JSON string of interests
    bio = db.Column(db.Text, nullable=True)  # Open text field
    profile_image = db.Column(db.String(500), nullable=True)  # URL or path
    
    # Referral code for this user (for others to register through them)
    referral_code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    referrals_given = db.relationship('Referral', foreign_keys='Referral.referrer_id', 
                                      backref='referrer', lazy='dynamic')
    referrals_received = db.relationship('Referral', foreign_keys='Referral.referred_id', 
                                         backref='referred_user', lazy='dynamic')
    
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id',
                                   backref='sender', lazy='dynamic')
    
    matches_given = db.relationship('Match', foreign_keys='Match.user_id',
                                   backref='user', lazy='dynamic')
    matches_received = db.relationship('Match', foreign_keys='Match.liked_user_id',
                                      backref='liked_user', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
    
    @staticmethod
    def generate_referral_code():
        """Generate a unique referral code"""
        return secrets.token_urlsafe(12)
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary (without encrypted data unless specified)"""
        data = {
            'id': self.id,
            'age': self.age,
            'gender': self.gender,
            'location': self.location,
            'height': self.height,
            'employment_status': self.employment_status,
            'interests': self.interests,
            'bio': self.bio,
            'profile_image': self.profile_image,
            'referral_code': self.referral_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }
        
        if include_sensitive:
            # Note: These should be decrypted before returning
            data.update({
                'email_encrypted': self.email_encrypted,
                'full_name_encrypted': self.full_name_encrypted,
                'phone_encrypted': self.phone_encrypted,
                'address_encrypted': self.address_encrypted
            })
        
        return data


class Referral(db.Model):
    """Referral model - tracks who referred whom (tree structure)"""
    __tablename__ = 'referrals'
    
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    referred_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    referral_code_used = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'referrer_id': self.referrer_id,
            'referred_id': self.referred_id,
            'referral_code_used': self.referral_code_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Chat(db.Model):
    """Chat model - represents a conversation between two users"""
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='chat', lazy='dynamic', 
                              order_by='Message.sent_at.desc()')
    
    # Ensure unique chat between two users
    __table_args__ = (
        db.UniqueConstraint('user1_id', 'user2_id', name='unique_chat'),
    )
    
    def to_dict(self, current_user_id=None):
        last_message = self.messages.first()
        return {
            'id': self.id,
            'user1_id': self.user1_id,
            'user2_id': self.user2_id,
            'other_user_id': self.user2_id if current_user_id == self.user1_id else self.user1_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'last_message': last_message.to_dict() if last_message else None
        }


class Message(db.Model):
    """Message model - individual messages in a chat"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'sender_id': self.sender_id,
            'content': self.content,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'is_read': self.is_read
        }


class Match(db.Model):
    """Match model - tracks likes/matches between users"""
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    liked_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_mutual = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure a user can only like another user once
    __table_args__ = (
        db.UniqueConstraint('user_id', 'liked_user_id', name='unique_match'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'liked_user_id': self.liked_user_id,
            'is_mutual': self.is_mutual,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

