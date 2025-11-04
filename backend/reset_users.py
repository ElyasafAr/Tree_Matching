"""
Reset database - delete all users and referrals
WARNING: This will delete ALL data!
"""
from app import create_app
from models import db, User, Referral, Chat, Message, Match

def reset_database():
    app = create_app()
    
    with app.app_context():
        print("⚠️  WARNING: This will delete ALL data from the database!")
        print("Deleting all records...")
        
        # Delete in order (foreign key dependencies)
        Message.query.delete()
        Chat.query.delete()
        Match.query.delete()
        Referral.query.delete()
        User.query.delete()
        
        db.session.commit()
        
        print("✅ All data deleted successfully!")
        print("\nNext step: Run 'python create_first_user.py' to create your first user")

if __name__ == '__main__':
    reset_database()

