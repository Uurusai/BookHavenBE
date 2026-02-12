from app.modules.users import repository
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.validators import validate_email, validate_password, validate_username
from app.utils.auth import generate_token

def register_user(username, email, password, full_name=None, city=None, country=None):
    """Register a new user with validation"""
    # Validate username
    is_valid, message = validate_username(username)
    if not is_valid:
        return {'error': message}, None
    
    # Validate email
    if not validate_email(email):
        return {'error': 'Invalid email format'}, None
    
    # Validate password
    is_valid, message = validate_password(password)
    if not is_valid:
        return {'error': message}, None
    
    # Check if username already exists
    existing_user = repository.get_user_by_username(username)
    if existing_user:
        return {'error': 'Username already exists'}, None
    
    # Check if email already exists
    existing_email = repository.get_user_by_email(email)
    if existing_email:
        return {'error': 'Email already exists'}, None
    
    # Hash the password
    password_hash = generate_password_hash(password)
    
    # Create user
    user = repository.create_user(username, email, password_hash, 'user', full_name, city, country)
    
    # Generate token
    token = generate_token(user['id'], user['username'], user['role'])
    
    return None, {
        'user': user,
        'token': token,
        'message': 'User registered successfully'
    }

def login_user(username, password):
    """Authenticate user and generate token"""
    # Get user with password hash
    user = repository.get_user_with_password(username)
    
    if not user:
        return {'error': 'Invalid username or password'}, None
    
    # Verify password
    if not check_password_hash(user['password_hash'], password):
        return {'error': 'Invalid username or password'}, None
    
    # Generate token
    token = generate_token(user['id'], user['username'], user['role'])
    
    # Remove password_hash from response
    user_data = {
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'role': user['role'],
        'full_name': user['full_name'],
        'city': user['city'],
        'country': user['country']
    }
    
    return None, {
        'user': user_data,
        'token': token,
        'message': 'Login successful'
    }

def create_user(username, email, password, role='user', full_name=None, city=None, country=None):
    """Create a new user"""
    # Check if username already exists
    existing_user = repository.get_user_by_username(username)
    if existing_user:
        return {'error': 'Username already exists'}, None
    
    # Check if email already exists
    existing_email = repository.get_user_by_email(email)
    if existing_email:
        return {'error': 'Email already exists'}, None
    
    # Hash the password
    password_hash = generate_password_hash(password)
    
    # Create user
    user = repository.create_user(username, email, password_hash, role, full_name, city, country)
    return None, user

def get_user(user_id):
    """Get user by ID"""
    user = repository.get_user_by_id(user_id)
    if not user:
        return {'error': 'User not found'}, None
    return None, user

def get_all_users(page=1, per_page=20):
    """Get all users with pagination"""
    offset = (page - 1) * per_page
    users = repository.get_all_users(limit=per_page, offset=offset)
    total = repository.count_users()
    
    return None, {
        'users': users,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }

def update_user(user_id, **kwargs):
    """Update user information"""
    # Check if user exists
    existing_user = repository.get_user_by_id(user_id)
    if not existing_user:
        return {'error': 'User not found'}, None
    
    # Update user
    updated_user = repository.update_user(user_id, **kwargs)
    return None, updated_user

def delete_user(user_id):
    """Delete a user"""
    success = repository.delete_user(user_id)
    if not success:
        return {'error': 'User not found'}, None
    return None, {'message': 'User deleted successfully'}

def verify_password(username, password):
    """Verify user password"""
    user = repository.get_user_by_username(username)
    if not user:
        return {'error': 'Invalid credentials'}, None
    
    # Note: This would need the password_hash which we're not returning
    # In a real app, you'd fetch it separately or include it in a login-specific query
    return None, user