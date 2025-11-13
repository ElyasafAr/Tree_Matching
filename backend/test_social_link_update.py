# -*- coding: utf-8 -*-
"""
Test script to manually update social_link for a user and verify it's saved
Run: python3 test_social_link_update.py <user_id> <social_link_value>
Example: python3 test_social_link_update.py 1 https://instagram.com/test
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    sys.exit(1)

if len(sys.argv) < 3:
    print("Usage: python3 test_social_link_update.py <user_id> <social_link_value>")
    print("Example: python3 test_social_link_update.py 1 https://instagram.com/test")
    sys.exit(1)

user_id = sys.argv[1]
social_link_value = sys.argv[2]

print(f"Testing social_link update for user_id: {user_id}")
print(f"Setting social_link to: '{social_link_value}'")

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get current value
        result = conn.execute(text("SELECT id, social_link FROM users WHERE id = :user_id"), {"user_id": user_id})
        row = result.fetchone()
        
        if not row:
            print(f"ERROR: User with id {user_id} not found!")
            sys.exit(1)
        
        print(f"\nBefore update:")
        print(f"  User ID: {row[0]}")
        print(f"  Current social_link: '{row[1] if row[1] else 'NULL/EMPTY'}'")
        
        # Update
        conn.execute(text("UPDATE users SET social_link = :social_link WHERE id = :user_id"), {
            "social_link": social_link_value if social_link_value.strip() else None,
            "user_id": user_id
        })
        conn.commit()
        
        print(f"\nUpdate executed. Committed.")
        
        # Verify
        result = conn.execute(text("SELECT id, social_link FROM users WHERE id = :user_id"), {"user_id": user_id})
        row = result.fetchone()
        
        print(f"\nAfter update:")
        print(f"  User ID: {row[0]}")
        print(f"  social_link: '{row[1] if row[1] else 'NULL/EMPTY'}'")
        
        if row[1] == social_link_value:
            print("\nSUCCESS: social_link was saved correctly!")
        else:
            print(f"\nWARNING: Expected '{social_link_value}' but got '{row[1] if row[1] else 'NULL/EMPTY'}'")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

