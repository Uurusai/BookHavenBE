from app.modules.transactions import repository

def create_transaction(status, final_price, buyer_id, seller_id, book_offer_id):
    """Create a new transaction"""
    # Create transaction
    transaction = repository.create_transaction(status, final_price, buyer_id, 
                                               seller_id, book_offer_id)
    return None, transaction

def get_transaction(transaction_id):
    """Get transaction by ID"""
    transaction = repository.get_transaction_by_id(transaction_id)
    if not transaction:
        return {'error': 'Transaction not found'}, None
    return None, transaction

def get_all_transactions(page=1, per_page=20, status=None):
    """Get all transactions with pagination and optional status filter"""
    offset = (page - 1) * per_page
    transactions = repository.get_all_transactions(limit=per_page, offset=offset, status=status)
    total = repository.count_transactions(status=status)
    
    return None, {
        'transactions': transactions,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
    }

def get_buyer_transactions(buyer_id, page=1, per_page=20):
    """Get all transactions for a specific buyer"""
    offset = (page - 1) * per_page
    transactions = repository.get_transactions_by_buyer(buyer_id, limit=per_page, offset=offset)
    
    return None, {
        'transactions': transactions,
        'page': page,
        'per_page': per_page
    }

def get_seller_transactions(seller_id, page=1, per_page=20):
    """Get all transactions for a specific seller"""
    offset = (page - 1) * per_page
    transactions = repository.get_transactions_by_seller(seller_id, limit=per_page, offset=offset)
    
    return None, {
        'transactions': transactions,
        'page': page,
        'per_page': per_page
    }

def get_offer_transactions(book_offer_id, page=1, per_page=20):
    """Get all transactions for a specific book offer"""
    offset = (page - 1) * per_page
    transactions = repository.get_transactions_by_offer(book_offer_id, limit=per_page, offset=offset)
    
    return None, {
        'transactions': transactions,
        'page': page,
        'per_page': per_page
    }

def update_transaction(transaction_id, **kwargs):
    """Update transaction information"""
    # Check if transaction exists
    existing_transaction = repository.get_transaction_by_id(transaction_id)
    if not existing_transaction:
        return {'error': 'Transaction not found'}, None
    
    # Update transaction
    updated_transaction = repository.update_transaction(transaction_id, **kwargs)
    return None, updated_transaction

def delete_transaction(transaction_id):
    """Delete a transaction"""
    success = repository.delete_transaction(transaction_id)
    if not success:
        return {'error': 'Transaction not found'}, None
    return None, {'message': 'Transaction deleted successfully'}
