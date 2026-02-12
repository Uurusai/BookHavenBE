from flask import Blueprint, request, jsonify
from app.modules.chat import service

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Chat Thread routes
@chat_bp.route('/threads', methods=['GET'])
def get_chat_threads():
    """Get all chat threads with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    error, result = service.get_all_chat_threads(page=page, per_page=per_page)
    
    if error:
        return jsonify(error), 400
    
    return jsonify(result), 200

@chat_bp.route('/threads/<int:thread_id>', methods=['GET'])
def get_chat_thread(thread_id):
    """Get chat thread by ID"""
    error, thread = service.get_chat_thread(thread_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(thread), 200

@chat_bp.route('/threads', methods=['POST'])
def create_chat_thread():
    """Create a new chat thread"""
    error, thread = service.create_chat_thread()
    
    if error:
        return jsonify(error), 400
    
    return jsonify(thread), 201

@chat_bp.route('/threads/<int:thread_id>', methods=['DELETE'])
def delete_chat_thread(thread_id):
    """Delete a chat thread"""
    error, result = service.delete_chat_thread(thread_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(result), 200

# Chat Message routes
@chat_bp.route('/threads/<int:thread_id>/messages', methods=['GET'])
def get_thread_messages(thread_id):
    """Get all messages in a thread"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    error, result = service.get_thread_messages(thread_id, page=page, per_page=per_page)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(result), 200

@chat_bp.route('/messages/<int:message_id>', methods=['GET'])
def get_chat_message(message_id):
    """Get chat message by ID"""
    error, message = service.get_chat_message(message_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(message), 200

@chat_bp.route('/messages', methods=['POST'])
def create_chat_message():
    """Create a new chat message"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['message', 'sender_id', 'thread_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields: message, sender_id, thread_id'}), 400
    
    error, message = service.create_chat_message(
        message=data['message'],
        sender_id=data['sender_id'],
        thread_id=data['thread_id']
    )
    
    if error:
        return jsonify(error), 400
    
    return jsonify(message), 201

@chat_bp.route('/messages/<int:message_id>', methods=['PUT', 'PATCH'])
def update_chat_message(message_id):
    """Update a chat message"""
    data = request.get_json()
    
    if 'message' not in data:
        return jsonify({'error': 'Missing required field: message'}), 400
    
    error, message = service.update_chat_message(message_id, data['message'])
    
    if error:
        return jsonify(error), 404
    
    return jsonify(message), 200

@chat_bp.route('/messages/<int:message_id>', methods=['DELETE'])
def delete_chat_message(message_id):
    """Delete a chat message"""
    error, result = service.delete_chat_message(message_id)
    
    if error:
        return jsonify(error), 404
    
    return jsonify(result), 200
