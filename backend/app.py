from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from auth import auth_bp
from routes.users import users_bp
from routes.chat import chat_bp
from routes.referrals import referrals_bp

def create_app():
    """Application factory for Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)  # Enable CORS for all routes
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(referrals_bp)
    
    # Health check endpoint
    @app.route('/')
    def health_check():
        return jsonify({
            'status': 'ok',
            'message': 'Tree Matching API is running'
        })
    
    # TEMPORARY: Reset database endpoint (REMOVE AFTER USE!)
    @app.route('/admin/reset-database-DANGER', methods=['POST'])
    def reset_database():
        """WARNING: Deletes ALL data from database!"""
        try:
            from models import User, Referral, Chat, Message, Match
            
            # Delete all records
            Message.query.delete()
            Chat.query.delete()
            Match.query.delete()
            Referral.query.delete()
            User.query.delete()
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'All data deleted! Now create first user.'
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # TEMPORARY: Create first user endpoint with admin password (REMOVE AFTER USE!)
    @app.route('/api/secret-initialize-system', methods=['POST'])
    def create_first_user_endpoint():
        """Create first user without referral code - requires admin password"""
        try:
            import bcrypt
            from models import User
            from encryption import encryption_service
            import os
            
            data = request.get_json()
            
            # Require admin password
            admin_password = os.getenv('ADMIN_SETUP_PASSWORD', 'TreeMatching2024!')
            if data.get('admin_password') != admin_password:
                return jsonify({'error': 'Invalid admin password'}), 403
            
            # Validate
            if not data.get('email') or not data.get('password') or not data.get('full_name'):
                return jsonify({'error': 'Email, password, and full_name required'}), 400
            
            # Check if users exist
            existing_users = User.query.count()
            if existing_users > 0:
                return jsonify({
                    'error': f'System already initialized. {existing_users} user(s) exist.'
                }), 400
            
            # Hash password
            password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Encrypt sensitive fields
            email_encrypted = encryption_service.encrypt(data['email'].lower().strip())
            full_name_encrypted = encryption_service.encrypt(data['full_name'])
            
            # Create user
            user = User(
                email_encrypted=email_encrypted,
                full_name_encrypted=full_name_encrypted,
                password_hash=password_hash
            )
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'First user created successfully!',
                'referral_code': user.referral_code,
                'user_id': user.id,
                'email': data['email']
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/health')
    def api_health():
        return jsonify({
            'status': 'ok',
            'message': 'API is healthy'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({'error': 'Missing authorization token'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

# Create app instance for gunicorn
app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

