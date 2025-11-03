"""
Initialize the database - create all tables
"""
from app import create_app
from models import db

def init_database():
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        print("\nNext step: Run 'python create_first_user.py' to create your first user")

if __name__ == '__main__':
    init_database()

