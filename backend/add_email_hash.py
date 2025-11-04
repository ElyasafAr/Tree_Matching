"""
Add email_hash column to existing users table
This is a one-time migration script
"""
from app import create_app
from models import db
from sqlalchemy import text

def add_email_hash_column():
    app = create_app()
    
    with app.app_context():
        print("Adding email_hash column to users table...")
        
        try:
            # Add column if it doesn't exist
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS email_hash VARCHAR(64) UNIQUE;
            """))
            
            # Create index
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_email_hash 
                ON users(email_hash);
            """))
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            print("\nAlternative: Drop and recreate tables with init_db.py")

if __name__ == '__main__':
    add_email_hash_column()

