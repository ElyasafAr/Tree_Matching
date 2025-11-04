"""
Script to create the first user (root user) without a referral code requirement.
This user can then refer other users.
"""
import bcrypt
from app import create_app
from models import db, User
from encryption import encryption_service

def create_first_user():
    app = create_app()
    
    with app.app_context():
        # Check if any users exist
        if User.query.first():
            print("Users already exist in the database!")
            print("First user should only be created once.")
            return
        
        print("Creating first user (root)...")
        
        # Get user details
        email = input("Enter email: ")
        password = input("Enter password: ")
        full_name = input("Enter full name: ")
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Encrypt and hash email
        email_normalized = email.lower().strip()
        email_hash = encryption_service.hash_email(email_normalized)
        email_encrypted = encryption_service.encrypt(email_normalized)
        full_name_encrypted = encryption_service.encrypt(full_name)
        
        # Create user
        user = User(
            email_hash=email_hash,
            email_encrypted=email_encrypted,
            full_name_encrypted=full_name_encrypted,
            password_hash=password_hash
        )
        
        db.session.add(user)
        db.session.commit()
        
        print(f"\n✅ First user created successfully!")
        print(f"Referral Code: {user.referral_code}")
        print(f"\nShare this code with others so they can register!")
        print(f"Login with: {email}")

if __name__ == '__main__':
    create_first_user()

