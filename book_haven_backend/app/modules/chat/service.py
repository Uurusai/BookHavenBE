from app.modules.chat import repository

# Chat Thread services
def create_chat_thread():
    """Create a new chat thread"""
    thread = repository.create_chat_thread()
    return None, thread

def get_chat_thread(thread_id):
    """Get chat thread by ID"""
    thread = repository.get_chat_thread_by_id(thread_id)
    if not thread:
        return {'error': 'Chat thread not found'}, None
    return None, thread

def get_all_chat_threads(page=1, per_page=20):
    """Get all chat threads with pagination"""
    offset = (page - 1) * per_page
    threads = repository.get_all_chat_threads(limit=per_page, offset=offset)
    total = repository.count_chat_threads()
    
    return None, {
        'threads': threads,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
    }

def delete_chat_thread(thread_id):
    """Delete a chat thread"""
    success = repository.delete_chat_thread(thread_id)
    if not success:
        return {'error': 'Chat thread not found'}, None
    return None, {'message': 'Chat thread deleted successfully'}

# Chat Message services
def create_chat_message(message, sender_id, thread_id):
    """Create a new chat message"""
    # Verify thread exists
    thread = repository.get_chat_thread_by_id(thread_id)
    if not thread:
        return {'error': 'Chat thread not found'}, None
    
    # Create message
    chat_message = repository.create_chat_message(message, sender_id, thread_id)
    return None, chat_message

def get_chat_message(message_id):
    """Get chat message by ID"""
    message = repository.get_chat_message_by_id(message_id)
    if not message:
        return {'error': 'Chat message not found'}, None
    return None, message

def get_thread_messages(thread_id, page=1, per_page=50):
    """Get all messages in a thread with pagination"""
    # Verify thread exists
    thread = repository.get_chat_thread_by_id(thread_id)
    if not thread:
        return {'error': 'Chat thread not found'}, None
    
    offset = (page - 1) * per_page
    messages = repository.get_messages_by_thread(thread_id, limit=per_page, offset=offset)
    total = repository.count_messages_in_thread(thread_id)
    
    return None, {
        'messages': messages,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
    }

def update_chat_message(message_id, message):
    """Update a chat message"""
    # Check if message exists
    existing_message = repository.get_chat_message_by_id(message_id)
    if not existing_message:
        return {'error': 'Chat message not found'}, None
    
    # Update message
    updated_message = repository.update_chat_message(message_id, message)
    return None, updated_message

def delete_chat_message(message_id):
    """Delete a chat message"""
    success = repository.delete_chat_message(message_id)
    if not success:
        return {'error': 'Chat message not found'}, None
    return None, {'message': 'Chat message deleted successfully'}
