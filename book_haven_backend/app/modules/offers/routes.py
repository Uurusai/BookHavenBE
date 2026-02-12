from flask import Blueprint, request, jsonify
from app.modules.offers import service

offers_bp = Blueprint('offers', __name__, url_prefix='/api/offers')

@offers_bp.route('', methods=['GET'])
def get_book_offers():
    """Get all book offers with pagination and optional filters"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offer_type = request.args.get('offer_type', None, type=str)
    is_active = request.args.get('is_active', None, type=lambda v: v.lower() == 'true')
    
    error, result = service.get_all_book_offers(page=page, per_page=per_page, 
                                                offer_type=offer_type, is_active=is_active)
    
    if error:
        return jsonify(error), 400
    
    return jsonify(result), 200

@offers_bp.route('/<int:offer_id>', methods=['GET'])
def get_book_offer(offer_id):
    """Get book offer by ID"""
    error, offer = service.get_book_offer(offer_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(offer), 200

@offers_bp.route('', methods=['POST'])
def create_book_offer():
    """Create a new book offer"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['offer_type', 'price', 'condition', 'quantity', 'user_id', 'book_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': f'Missing required fields: {", ".join(required_fields)}'}), 400
    
    error, offer = service.create_book_offer(
        offer_type=data['offer_type'],
        price=data['price'],
        condition=data['condition'],
        quantity=data['quantity'],
        user_id=data['user_id'],
        book_id=data['book_id'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        is_active=data.get('is_active', True)
    )
    
    if error:
        return jsonify(error), 400
    
    return jsonify(offer), 201

@offers_bp.route('/<int:offer_id>', methods=['PUT', 'PATCH'])
def update_book_offer(offer_id):
    """Update book offer information"""
    data = request.get_json()
    
    error, offer = service.update_book_offer(offer_id, **data)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(offer), 200

@offers_bp.route('/<int:offer_id>', methods=['DELETE'])
def delete_book_offer(offer_id):
    """Delete a book offer"""
    error, result = service.delete_book_offer(offer_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(result), 200

@offers_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_offers(user_id):
    """Get all offers by a specific user"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    error, result = service.get_user_offers(user_id, page=page, per_page=per_page)
    
    if error:
        return jsonify(error), 400
    
    return jsonify(result), 200

@offers_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book_offers_by_book(book_id):
    """Get all offers for a specific book"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    is_active = request.args.get('is_active', None, type=lambda v: v.lower() == 'true')
    
    error, result = service.get_book_offers(book_id, page=page, per_page=per_page, 
                                           is_active=is_active)
    
    if error:
        return jsonify(error), 400
    
    return jsonify(result), 200
