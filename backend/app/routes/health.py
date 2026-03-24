"""Health check route"""
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'RepoShield-AI v2'
    })
