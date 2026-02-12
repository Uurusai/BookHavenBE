import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from app.modules.users import repository

def generate_token(user_id, username, role):
    """Generate JWT token for authenticated user"""
    try:
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),  # Token expires in 7 days
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token
    except Exception as e:
        return None

def decode_token(token):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}

def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format. Use: Bearer <token>'}), 401
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        # Decode token
        payload = decode_token(token)
        
        if 'error' in payload:
            return jsonify({'error': payload['error']}), 401
        
        # Add user info to request context
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated

def role_required(*allowed_roles):
    """Decorator to restrict access to specific roles"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            user_role = request.current_user.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator

def get_current_user():
    """Get current authenticated user from token"""
    if hasattr(request, 'current_user'):
        user_id = request.current_user.get('user_id')
        return repository.get_user_by_id(user_id)
    return None
