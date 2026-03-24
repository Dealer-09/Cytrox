"""User routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'avatar_url': user.avatar_url,
        'subscription_tier': user.subscription_tier,
        'created_at': user.created_at.isoformat()
    })

@users_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    """Get or update user profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'PUT':
        data = request.json
        if 'email' in data:
            user.email = data['email']
        db.session.commit()
        return jsonify({'message': 'Profile updated'})
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'avatar_url': user.avatar_url,
        'subscription_tier': user.subscription_tier,
        'subscription_active': user.subscription_active
    })
