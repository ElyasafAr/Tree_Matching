# -*- coding: utf-8 -*-
"""
Test script to check if social_link is returned in to_dict() and jsonify
Run: python3 test_social_link_response.py <user_id>
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import json

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python3 test_social_link_response.py <user_id>")
    sys.exit(1)

user_id = sys.argv[1]

print(f"Testing social_link response for user_id: {user_id}")

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get user from DB
        result = conn.execute(text("SELECT id, social_link FROM users WHERE id = :user_id"), {"user_id": user_id})
        row = result.fetchone()
        
        if not row:
            print(f"ERROR: User {user_id} not found!")
            sys.exit(1)
        
        print(f"\nDirect DB query:")
        print(f"  User ID: {row[0]}")
        print(f"  social_link: '{row[1] if row[1] else 'NULL/EMPTY'}'")
        print(f"  social_link type: {type(row[1])}")
        print(f"  social_link is None: {row[1] is None}")
        
        # Test to_dict() manually
        print(f"\nTesting to_dict() simulation:")
        test_dict = {
            'id': row[0],
            'social_link': row[1]
        }
        print(f"  test_dict: {test_dict}")
        print(f"  'social_link' in test_dict: {'social_link' in test_dict}")
        print(f"  test_dict.get('social_link'): {test_dict.get('social_link')}")
        
        # Test jsonify simulation
        print(f"\nTesting JSON serialization:")
        json_str = json.dumps(test_dict)
        print(f"  JSON string: {json_str}")
        json_parsed = json.loads(json_str)
        print(f"  Parsed back: {json_parsed}")
        print(f"  'social_link' in parsed: {'social_link' in json_parsed}")
        print(f"  parsed.get('social_link'): {json_parsed.get('social_link')}")
        
        # Test with None
        print(f"\nTesting with None value:")
        test_dict_none = {
            'id': row[0],
            'social_link': None
        }
        json_str_none = json.dumps(test_dict_none)
        print(f"  JSON with None: {json_str_none}")
        json_parsed_none = json.loads(json_str_none)
        print(f"  Parsed back: {json_parsed_none}")
        print(f"  'social_link' in parsed: {'social_link' in json_parsed_none}")
        print(f"  parsed.get('social_link'): {json_parsed_none.get('social_link')}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

