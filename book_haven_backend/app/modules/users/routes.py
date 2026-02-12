from flask import Blueprint, request, jsonify
from app.modules.users import service
from app.utils.auth import token_required, role_required, get_current_user

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields: username, email, password'}), 400
    
    error, result = service.register_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        full_name=data.get('full_name'),
        city=data.get('city'),
        country=data.get('country')
    )
    
    if error:
        return jsonify(error), 400
    
    return jsonify(result), 201

@users_bp.route('/login', methods=['POST'])
def login():
    """Login user and return token"""
    data = request.get_json()
    
    required_fields = ['username', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields: username, password'}), 400
    
    error, result = service.login_user(
        username=data['username'],
        password=data['password']
    )
    
    if error:
        return jsonify(error), 401
    
    return jsonify(result), 200

@users_bp.route('/me', methods=['GET'])
@token_required
def get_current_user_info():
    """Get current authenticated user info"""
    user = get_current_user()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user), 200

@users_bp.route('/me', methods=['PUT', 'PATCH'])
@token_required
def update_current_user():
    """Update current authenticated user info"""
    data = request.get_json()
    user_id = request.current_user.get('user_id')
    
    # Prevent changing role through this endpoint
    if 'role' in data:
        del data['role']
    
    error, user = service.update_user(user_id, **data)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(user), 200

# Admin routes
@users_bp.route('', methods=['GET'])
@role_required('admin')
def get_users():
    """Get all users with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    error, result = service.get_all_users(page=page, per_page=per_page)
    
    if error:
        return jsonify(error), 400
    
    return jsonify(result), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get user by ID"""
    error, user = service.get_user(user_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(user), 200

@users_bp.route('', methods=['POST'])
@role_required('admin')
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields: username, email, password'}), 400
    
    error, user = service.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        role=data.get('role', 'user'),
        full_name=data.get('full_name'),
        city=data.get('city'),
        country=data.get('country')
    )
    
    if error:
        return jsonify(error), 400
    
    return jsonify(user), 201

@role_required('admin')
@users_bp.route('/<int:user_id>', methods=['PUT', 'PATCH'])
def update_user(user_id):
    """Update user information"""
    data = request.get_json()
    
    error, user = service.update_user(user_id, **data)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(user), 200

@role_required('admin')
@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    error, result = service.delete_user(user_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(result), 200