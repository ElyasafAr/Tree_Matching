from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from auth import auth_bp
from routes.users import users_bp
from routes.chat import chat_bp
from routes.referrals import referrals_bp
from routes.upload import upload_bp

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
    app.register_blueprint(upload_bp)
    
    # Health check endpoint
    @app.route('/')
    def health_check():
        return jsonify({
            'status': 'ok',
            'message': 'Tree Matching API is running'
        })
    
    # TEMPORARY: Migration endpoint (REMOVE AFTER USE!)
    @app.route('/admin/migrate-add-email-hash', methods=['POST'])
    def migrate_add_email_hash():
        """Add email_hash column to users table"""
        try:
            from sqlalchemy import text
            import os
            
            data = request.get_json() or {}
            admin_password = os.getenv('ADMIN_SETUP_PASSWORD', 'TreeMatching2024!')
            
            if data.get('admin_password') != admin_password:
                return jsonify({'error': 'Invalid admin password'}), 403
            
            # Add column
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS email_hash VARCHAR(64);
            """))
            
            # Create index
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_email_hash 
                ON users(email_hash);
            """))
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Migration completed! Column added.'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
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
            import os
            from models import User
            from encryption import encryption_service
            from flask_jwt_extended import create_access_token
            
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
            
            # Encrypt and hash email
            email_normalized = data['email'].lower().strip()
            email_hash = encryption_service.hash_email(email_normalized)
            email_encrypted = encryption_service.encrypt(email_normalized)
            full_name_encrypted = encryption_service.encrypt(data['full_name'])
            
            # Create user
            user = User(
                email_hash=email_hash,
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
        print(f"[JWT ERROR] Unauthorized - Missing token: {callback}")
        return jsonify({'error': 'Missing authorization token'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        print(f"[JWT ERROR] Invalid token: {callback}")
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"[JWT ERROR] Token expired - payload: {jwt_payload}")
        return jsonify({'error': 'Token has expired'}), 401
    
    # Create database tables and run migrations
    with app.app_context():
        db.create_all()
        
        # Auto-migration: Add new columns if they don't exist
        try:
            from sqlalchemy import text, inspect
            
            # Check if table exists first
            inspector = inspect(db.engine)
            if 'users' in inspector.get_table_names():
                # Check if columns exist
                columns = [col['name'] for col in inspector.get_columns('users')]
                print(f"[MIGRATION] Existing columns in users table: {columns}")  # Debug log
                
                # Add height column if missing
                if 'height' not in columns:
                    db.session.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN height INTEGER;
                    """))
                    db.session.commit()
                    print("✅ Migration: Added 'height' column to users table")
                else:
                    print("ℹ️  Migration: 'height' column already exists")
                
                # Add employment_status column if missing
                if 'employment_status' not in columns:
                    db.session.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN employment_status VARCHAR(100);
                    """))
                    db.session.commit()
                    print("✅ Migration: Added 'employment_status' column to users table")
                else:
                    print("ℹ️  Migration: 'employment_status' column already exists")
                
                # Add religious_status column if missing
                if 'religious_status' not in columns:
                    try:
                        db.session.execute(text("""
                            ALTER TABLE users 
                            ADD COLUMN religious_status VARCHAR(100);
                        """))
                        db.session.commit()
                        print("✅ Migration: Added 'religious_status' column to users table")
                    except Exception as migration_error:
                        print(f"❌ Migration ERROR adding 'religious_status': {migration_error}")
                        import traceback
                        traceback.print_exc()
                        db.session.rollback()
                else:
                    print("ℹ️  Migration: 'religious_status' column already exists")
                
                # Add social_link column if missing
                if 'social_link' not in columns:
                    try:
                        db.session.execute(text("""
                            ALTER TABLE users 
                            ADD COLUMN social_link VARCHAR(500);
                        """))
                        db.session.commit()
                        print("✅ Migration: Added 'social_link' column to users table")
                    except Exception as migration_error:
                        print(f"❌ Migration ERROR adding 'social_link': {migration_error}")
                        import traceback
                        traceback.print_exc()
                        db.session.rollback()
                else:
                    print("ℹ️  Migration: 'social_link' column already exists")
                
                # Add is_suspended column if missing
                if 'is_suspended' not in columns:
                    try:
                        db.session.execute(text("""
                            ALTER TABLE users 
                            ADD COLUMN is_suspended BOOLEAN DEFAULT FALSE;
                        """))
                        db.session.commit()
                        print("✅ Migration: Added 'is_suspended' column to users table")
                    except Exception as migration_error:
                        print(f"❌ Migration ERROR adding 'is_suspended': {migration_error}")
                        import traceback
                        traceback.print_exc()
                        db.session.rollback()
                else:
                    print("ℹ️  Migration: 'is_suspended' column already exists")
                
                # Create blocks table if it doesn't exist
                if 'blocks' not in inspector.get_table_names():
                    try:
                        db.session.execute(text("""
                            CREATE TABLE blocks (
                                id SERIAL PRIMARY KEY,
                                blocker_id INTEGER NOT NULL REFERENCES users(id),
                                blocked_id INTEGER NOT NULL REFERENCES users(id),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                UNIQUE(blocker_id, blocked_id)
                            );
                        """))
                        db.session.commit()
                        print("✅ Migration: Created 'blocks' table")
                    except Exception as migration_error:
                        print(f"❌ Migration ERROR creating 'blocks' table: {migration_error}")
                        import traceback
                        traceback.print_exc()
                        db.session.rollback()
                else:
                    print("ℹ️  Migration: 'blocks' table already exists")
            else:
                # Table doesn't exist yet, db.create_all() will create it with all columns
                print("ℹ️  Users table doesn't exist yet, will be created with all columns")
                
        except Exception as e:
            # Don't fail startup if migration fails (might be permission issue)
            print(f"⚠️  Migration check failed (non-critical): {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
    
    return app

# Create app instance for gunicorn
app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

