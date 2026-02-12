from flask import Blueprint, request, jsonify
from app.modules.transactions import service

transactions_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

@transactions_bp.route('', methods=['GET'])
def get_transactions():
    """Get all transactions with pagination and optional status filter"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None, type=str)
    
    error, result = service.get_all_transactions(page=page, per_page=per_page, status=status)
    
    if error:
        return jsonify(error), 400
    
    return jsonify(result), 200

@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get transaction by ID"""
    error, transaction = service.get_transaction(transaction_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(transaction), 200

@transactions_bp.route('', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['status', 'final_price', 'buyer_id', 'seller_id', 'book_offer_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': f'Missing required fields: {", ".join(required_fields)}'}), 400
    
    error, transaction = service.create_transaction(
        status=data['status'],
        final_price=data['final_price'],
        buyer_id=data['buyer_id'],
        seller_id=data['seller_id'],
        book_offer_id=data['book_offer_id']
    )
    
    if error:
        return jsonify(error), 400
    
    return jsonify(transaction), 201

@transactions_bp.route('/<int:transaction_id>', methods=['PUT', 'PATCH'])
def update_transaction(transaction_id):
    """Update transaction information"""
    data = request.get_json()
    
    error, transaction = service.update_transaction(transaction_id, **data)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(transaction), 200

@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete a transaction"""
    error, result = service.delete_transaction(transaction_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(result), 200

@transactions_bp.route('/buyers/<int:buyer_id>', methods=['GET'])
def get_buyer_transactions(buyer_id):
    """Get all transactions for a specific buyer"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    error, result = service.get_buyer_transactions(buyer_id, page=page, per_page=per_page)
    
    if error:
        return jsonify(error), 400
    
    return jsonify(result), 200

@transactions_bp.route('/sellers/<int:seller_id>', methods=['GET'])
def get_seller_transactions(seller_id):
    """Get all transactions for a specific seller"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    error, result = service.get_seller_transactions(seller_id, page=page, per_page=per_page)
    
    if error:
        return jsonify(error), 400
    
    return jsonify(result), 200

@transactions_bp.route('/offers/<int:book_offer_id>', methods=['GET'])
def get_offer_transactions(book_offer_id):
    """Get all transactions for a specific book offer"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    error, result = service.get_offer_transactions(book_offer_id, page=page, per_page=per_page)
    
    if error:
        return jsonify(error), 400
    
    return jsonify(result), 200
