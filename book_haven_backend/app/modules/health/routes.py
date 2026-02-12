from flask import Blueprint, jsonify
from app.modules.health import services

health_bp = Blueprint('health', __name__, url_prefix='/api/health')

@health_bp.route('', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        health_status = services.get_health_status()
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503