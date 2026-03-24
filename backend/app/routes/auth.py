"""Authentication routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import requests
import os
from app import db
from app.models import User
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/github/login', methods=['GET'])
def github_login():
    """Initiate GitHub OAuth flow"""
    client_id = os.getenv('GITHUB_CLIENT_ID')
    redirect_uri = request.args.get('redirect_uri', 'http://localhost:5173/auth/github/callback')
    
    github_auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=read:user%20user:email%20repo"
    )
    
    return jsonify({'auth_url': github_auth_url})

@auth_bp.route('/github/callback', methods=['POST'])
def github_callback():
    """Handle GitHub OAuth callback"""
    code = request.json.get('code')
    
    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400
    
    # Exchange code for access token
    token_resp = requests.post('https://github.com/login/oauth/access_token', {
        'client_id': os.getenv('GITHUB_CLIENT_ID'),
        'client_secret': os.getenv('GITHUB_CLIENT_SECRET'),
        'code': code,
    }, headers={'Accept': 'application/json'})
    
    if token_resp.status_code != 200:
        return jsonify({'error': 'Failed to exchange code for token'}), 400
    
    github_token = token_resp.json().get('access_token')
    
    # Get user info from GitHub
    user_resp = requests.get('https://api.github.com/user',
                            headers={'Authorization': f'Bearer {github_token}'})
    
    if user_resp.status_code != 200:
        return jsonify({'error': 'Failed to get user info'}), 400
    
    user_data = user_resp.json()
    
    # Find or create user
    user = User.query.filter_by(github_id=str(user_data['id'])).first()
    
    if not user:
        user = User(
            github_id=str(user_data['id']),
            username=user_data['login'],
            email=user_data['email'] or f"{user_data['login']}@github.com",
            avatar_url=user_data['avatar_url']
        )
        db.session.add(user)
        db.session.commit()
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create JWT tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar_url': user.avatar_url,
            'subscription_tier': user.subscription_tier
        }
    })

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token})

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'avatar_url': user.avatar_url,
        'subscription_tier': user.subscription_tier,
        'subscription_active': user.subscription_active,
        'created_at': user.created_at.isoformat()
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    return jsonify({'message': 'Logged out successfully'})
