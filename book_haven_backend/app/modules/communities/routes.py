from flask import Blueprint, request, jsonify
from app.modules.communities import service

communities_bp = Blueprint('communities', __name__, url_prefix='/api/communities')

# Community routes
@communities_bp.route('', methods=['GET'])
def get_communities():
    """Get all communities with pagination and optional search"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', None, type=str)
    
    error, result = service.get_all_communities(page=page, per_page=per_page, search=search)
    
    if error:
        return jsonify(error), 400
    
    return jsonify(result), 200

@communities_bp.route('/<int:community_id>', methods=['GET'])
def get_community(community_id):
    """Get community by ID"""
    error, community = service.get_community(community_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(community), 200

@communities_bp.route('', methods=['POST'])
def create_community():
    """Create a new community"""
    data = request.get_json()
    
    # Validate required fields
    if 'name' not in data:
        return jsonify({'error': 'Missing required field: name'}), 400
    
    error, community = service.create_community(
        name=data['name'],
        description=data.get('description')
    )
    
    if error:
        return jsonify(error), 400
    
    return jsonify(community), 201

@communities_bp.route('/<int:community_id>', methods=['PUT', 'PATCH'])
def update_community(community_id):
    """Update community information"""
    data = request.get_json()
    
    error, community = service.update_community(community_id, **data)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(community), 200

@communities_bp.route('/<int:community_id>', methods=['DELETE'])
def delete_community(community_id):
    """Delete a community"""
    error, result = service.delete_community(community_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(result), 200

# Membership routes
@communities_bp.route('/<int:community_id>/members', methods=['GET'])
def get_community_members(community_id):
    """Get all members of a community"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    error, result = service.get_community_members(community_id, page=page, per_page=per_page)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(result), 200

@communities_bp.route('/<int:community_id>/members', methods=['POST'])
def add_member(community_id):
    """Add a member to a community"""
    data = request.get_json()
    
    if 'user_id' not in data:
        return jsonify({'error': 'Missing required field: user_id'}), 400
    
    error, membership = service.add_member_to_community(
        user_id=data['user_id'],
        community_id=community_id,
        role=data.get('role', 'member')
    )
    
    if error:
        return jsonify(error), 400
    
    return jsonify(membership), 201

@communities_bp.route('/<int:community_id>/members/<int:user_id>', methods=['DELETE'])
def remove_member(community_id, user_id):
    """Remove a member from a community"""
    error, result = service.remove_member_from_community(user_id, community_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(result), 200

@communities_bp.route('/<int:community_id>/members/<int:user_id>', methods=['PATCH'])
def update_member_role(community_id, user_id):
    """Update a member's role in a community"""
    data = request.get_json()
    
    if 'role' not in data:
        return jsonify({'error': 'Missing required field: role'}), 400
    
    error, membership = service.update_member_role(user_id, community_id, data['role'])
    
    if error:
        return jsonify(error), 404
    
    return jsonify(membership), 200

@communities_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_communities(user_id):
    """Get all communities a user is member of"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    error, result = service.get_user_communities(user_id, page=page, per_page=per_page)
    
    if error:
        return jsonify(error), 400
    
    return jsonify(result), 200
