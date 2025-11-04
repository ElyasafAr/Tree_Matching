"""
Utility functions for the backend
"""
from flask_jwt_extended import get_jwt_identity

def get_current_user_id():
    """Helper to get current user ID as integer from JWT"""
    identity = get_jwt_identity()
    return int(identity) if identity else None

