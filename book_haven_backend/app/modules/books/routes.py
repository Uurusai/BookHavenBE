from flask import Blueprint, request, jsonify
from app.modules.books import service

books_bp = Blueprint('books', __name__, url_prefix='/api/books')

@books_bp.route('', methods=['GET'])
def get_books():
    """Get all books with pagination and optional search"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', None, type=str)
    
    error, result = service.get_all_books(page=page, per_page=per_page, search=search)
    
    if error:
        return jsonify(error), 400
    
    return jsonify(result), 200

@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get book by ID"""
    error, book = service.get_book(book_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(book), 200

@books_bp.route('', methods=['POST'])
def create_book():
    """Create a new book"""
    data = request.get_json()
    
    # Validate required fields
    if 'title' not in data:
        return jsonify({'error': 'Missing required field: title'}), 400
    
    error, book = service.create_book(
        isbn=data.get('isbn'),
        title=data['title'],
        author=data.get('author'),
        publisher=data.get('publisher'),
        category=data.get('category')
    )
    
    if error:
        return jsonify(error), 400
    
    return jsonify(book), 201

@books_bp.route('/<int:book_id>', methods=['PUT', 'PATCH'])
def update_book(book_id):
    """Update book information"""
    data = request.get_json()
    
    error, book = service.update_book(book_id, **data)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(book), 200

@books_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book"""
    error, result = service.delete_book(book_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(result), 200
