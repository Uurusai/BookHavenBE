from app.modules.offers import repository

def create_book_offer(offer_type, price, condition, quantity, user_id, book_id, 
                     latitude=None, longitude=None, is_active=True):
    """Create a new book offer"""
    # Validate offer_type
    if offer_type not in ['SELL', 'BUY']:
        return {'error': 'Invalid offer_type. Must be SELL or BUY'}, None
    
    # Create offer
    offer = repository.create_book_offer(offer_type, price, condition, quantity, 
                                        user_id, book_id, latitude, longitude, is_active)
    return None, offer

def get_book_offer(offer_id):
    """Get book offer by ID"""
    offer = repository.get_book_offer_by_id(offer_id)
    if not offer:
        return {'error': 'Book offer not found'}, None
    return None, offer

def get_all_book_offers(page=1, per_page=20, offer_type=None, is_active=None):
    """Get all book offers with pagination and optional filters"""
    offset = (page - 1) * per_page
    offers = repository.get_all_book_offers(limit=per_page, offset=offset, 
                                           offer_type=offer_type, is_active=is_active)
    total = repository.count_book_offers(offer_type=offer_type, is_active=is_active)
    
    return None, {
        'offers': offers,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
    }

def get_user_offers(user_id, page=1, per_page=20):
    """Get all offers by a specific user"""
    offset = (page - 1) * per_page
    offers = repository.get_offers_by_user(user_id, limit=per_page, offset=offset)
    
    return None, {
        'offers': offers,
        'page': page,
        'per_page': per_page
    }

def get_book_offers(book_id, page=1, per_page=20, is_active=None):
    """Get all offers for a specific book"""
    offset = (page - 1) * per_page
    offers = repository.get_offers_by_book(book_id, limit=per_page, offset=offset, 
                                          is_active=is_active)
    
    return None, {
        'offers': offers,
        'page': page,
        'per_page': per_page
    }

def update_book_offer(offer_id, **kwargs):
    """Update book offer information"""
    # Check if offer exists
    existing_offer = repository.get_book_offer_by_id(offer_id)
    if not existing_offer:
        return {'error': 'Book offer not found'}, None
    
    # Validate offer_type if provided
    if 'offer_type' in kwargs and kwargs['offer_type'] not in ['SELL', 'BUY']:
        return {'error': 'Invalid offer_type. Must be SELL or BUY'}, None
    
    # Update offer
    updated_offer = repository.update_book_offer(offer_id, **kwargs)
    return None, updated_offer

def delete_book_offer(offer_id):
    """Delete a book offer"""
    success = repository.delete_book_offer(offer_id)
    if not success:
        return {'error': 'Book offer not found'}, None
    return None, {'message': 'Book offer deleted successfully'}
