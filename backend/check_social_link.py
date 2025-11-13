# -*- coding: utf-8 -*-
"""
Script to check if social_link column exists in database and if values are being saved
Run: python check_social_link.py
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    print("Please set DATABASE_URL in your .env file or environment")
    sys.exit(1)

print("Connecting to database...")
print(f"Database URL: {DATABASE_URL[:50]}...")  # Show first 50 chars only for security

try:
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create inspector
    inspector = inspect(engine)
    
    # Check if users table exists
    if 'users' not in inspector.get_table_names():
        print("ERROR: 'users' table does not exist!")
        sys.exit(1)
    
    print("OK: 'users' table exists")
    
    # Get all columns
    columns = [col['name'] for col in inspector.get_columns('users')]
    print(f"\nAll columns in 'users' table:")
    for col in columns:
        print(f"   - {col}")
    
    # Check if social_link column exists
    if 'social_link' in columns:
        print("\nOK: 'social_link' column EXISTS in database")
        
        # Get column info
        for col in inspector.get_columns('users'):
            if col['name'] == 'social_link':
                print(f"   Type: {col['type']}")
                print(f"   Nullable: {col['nullable']}")
                break
        
        # Check if there are any values
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(social_link) as users_with_social_link,
                    COUNT(CASE WHEN social_link IS NOT NULL AND social_link != '' THEN 1 END) as non_empty_social_links
                FROM users
            """))
            row = result.fetchone()
            
            print(f"\nStatistics:")
            print(f"   Total users: {row[0]}")
            print(f"   Users with social_link (including empty): {row[1]}")
            print(f"   Users with non-empty social_link: {row[2]}")
            
            # Show sample data
            result = conn.execute(text("""
                SELECT id, social_link 
                FROM users 
                WHERE social_link IS NOT NULL AND social_link != ''
                LIMIT 5
            """))
            rows = result.fetchall()
            
            if rows:
                print(f"\nSample social_link values (first 5):")
                for row in rows:
                    print(f"   User ID {row[0]}: {row[1]}")
            else:
                print(f"\nWARNING: No users have social_link values (all are NULL or empty)")
                
            # Show recent updates
            result = conn.execute(text("""
                SELECT id, social_link, created_at, last_active
                FROM users 
                ORDER BY last_active DESC NULLS LAST, created_at DESC
                LIMIT 3
            """))
            rows = result.fetchall()
            
            print(f"\nRecent users (last 3):")
            for row in rows:
                print(f"   User ID {row[0]}: social_link = {row[1] if row[1] else 'NULL/EMPTY'}")
                
    else:
        print("\nERROR: 'social_link' column DOES NOT EXIST in database!")
        print("\nSolution: The auto-migration should add it, but it seems it didn't run.")
        print("   You can manually add it with:")
        print("   ALTER TABLE users ADD COLUMN social_link VARCHAR(500);")
        sys.exit(1)
    
    print("\nCheck completed successfully!")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
