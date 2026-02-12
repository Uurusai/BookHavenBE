from app.modules.communities import repository

# Community services
def create_community(name, description=None):
    """Create a new community"""
    community = repository.create_community(name, description)
    return None, community

def get_community(community_id):
    """Get community by ID"""
    community = repository.get_community_by_id(community_id)
    if not community:
        return {'error': 'Community not found'}, None
    return None, community

def get_all_communities(page=1, per_page=20, search=None):
    """Get all communities with pagination and optional search"""
    offset = (page - 1) * per_page
    
    if search:
        communities = repository.search_communities(search, limit=per_page, offset=offset)
        total = len(communities)  # Simplified
    else:
        communities = repository.get_all_communities(limit=per_page, offset=offset)
        total = repository.count_communities()
    
    return None, {
        'communities': communities,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
    }

def update_community(community_id, **kwargs):
    """Update community information"""
    # Check if community exists
    existing_community = repository.get_community_by_id(community_id)
    if not existing_community:
        return {'error': 'Community not found'}, None
    
    # Update community
    updated_community = repository.update_community(community_id, **kwargs)
    return None, updated_community

def delete_community(community_id):
    """Delete a community"""
    success = repository.delete_community(community_id)
    if not success:
        return {'error': 'Community not found'}, None
    return None, {'message': 'Community deleted successfully'}

# Membership services
def add_member_to_community(user_id, community_id, role='member'):
    """Add a user to a community"""
    # Check if community exists
    community = repository.get_community_by_id(community_id)
    if not community:
        return {'error': 'Community not found'}, None
    
    # Add member
    membership = repository.add_member(user_id, community_id, role)
    if not membership:
        return {'error': 'User is already a member of this community'}, None
    
    return None, membership

def remove_member_from_community(user_id, community_id):
    """Remove a user from a community"""
    success = repository.remove_member(user_id, community_id)
    if not success:
        return {'error': 'Membership not found'}, None
    return None, {'message': 'Member removed successfully'}

def get_community_members(community_id, page=1, per_page=50):
    """Get all members of a community"""
    # Check if community exists
    community = repository.get_community_by_id(community_id)
    if not community:
        return {'error': 'Community not found'}, None
    
    offset = (page - 1) * per_page
    members = repository.get_community_members(community_id, limit=per_page, offset=offset)
    
    return None, {
        'members': members,
        'page': page,
        'per_page': per_page
    }

def get_user_communities(user_id, page=1, per_page=20):
    """Get all communities a user is member of"""
    offset = (page - 1) * per_page
    communities = repository.get_user_communities(user_id, limit=per_page, offset=offset)
    
    return None, {
        'communities': communities,
        'page': page,
        'per_page': per_page
    }

def update_member_role(user_id, community_id, role):
    """Update a member's role in a community"""
    membership = repository.update_member_role(user_id, community_id, role)
    if not membership:
        return {'error': 'Membership not found'}, None
    return None, membership
