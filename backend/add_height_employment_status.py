"""
Add height and employment_status columns to existing users table
This is a one-time migration script
"""
from app import create_app
from models import db
from sqlalchemy import text

def add_height_employment_status_columns():
    app = create_app()
    
    with app.app_context():
        print("Adding height and employment_status columns to users table...")
        
        try:
            # Add height column if it doesn't exist
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS height INTEGER;
            """))
            
            # Add employment_status column if it doesn't exist
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS employment_status VARCHAR(100);
            """))
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            print("   - Added 'height' column (INTEGER)")
            print("   - Added 'employment_status' column (VARCHAR(100))")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            print("\nAlternative: Drop and recreate tables with init_db.py")
            print("⚠️  WARNING: This will delete all existing data!")

if __name__ == '__main__':
    add_height_employment_status_columns()

