# -*- coding: utf-8 -*-
"""
Script to add social_link column to users table if it doesn't exist
Run: python3 add_social_link_column.py
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

try:
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create inspector
    inspector = inspect(engine)
    
    # Check if users table exists
    if 'users' not in inspector.get_table_names():
        print("ERROR: 'users' table does not exist!")
        sys.exit(1)
    
    # Get all columns
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    # Check if social_link column exists
    if 'social_link' in columns:
        print("OK: 'social_link' column already exists in database")
        sys.exit(0)
    
    # Add the column
    print("Adding 'social_link' column to 'users' table...")
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN social_link VARCHAR(500);
        """))
        conn.commit()
    
    print("SUCCESS: 'social_link' column added successfully!")
    
    # Verify it was added
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('users')]
    if 'social_link' in columns:
        print("VERIFIED: Column exists in database")
    else:
        print("WARNING: Column was added but verification failed")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

