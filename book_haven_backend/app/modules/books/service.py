from app.modules.books import repository

def create_book(isbn, title, author=None, publisher=None, category=None):
    """Create a new book"""
    # Check if book with ISBN already exists
    if isbn:
        existing_book = repository.get_book_by_isbn(isbn)
        if existing_book:
            return {'error': 'Book with this ISBN already exists'}, None
    
    # Create book
    book = repository.create_book(isbn, title, author, publisher, category)
    return None, book

def get_book(book_id):
    """Get book by ID"""
    book = repository.get_book_by_id(book_id)
    if not book:
        return {'error': 'Book not found'}, None
    return None, book

def get_all_books(page=1, per_page=20, search=None):
    """Get all books with pagination and optional search"""
    offset = (page - 1) * per_page
    
    if search:
        books = repository.search_books(search, limit=per_page, offset=offset)
        total = len(books)  
    else:
        books = repository.get_all_books(limit=per_page, offset=offset)
        total = repository.count_books()
    
    return None, {
        'books': books,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
    }

def update_book(book_id, **kwargs):
    """Update book information"""
    # Check if book exists
    existing_book = repository.get_book_by_id(book_id)
    if not existing_book:
        return {'error': 'Book not found'}, None
    
    # Update book
    updated_book = repository.update_book(book_id, **kwargs)
    return None, updated_book

def delete_book(book_id):
    """Delete a book"""
    success = repository.delete_book(book_id)
    if not success:
        return {'error': 'Book not found'}, None
    return None, {'message': 'Book deleted successfully'}
