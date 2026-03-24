"""Team collaboration routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Team, team_members
import re

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def teams():
    """Get or create teams"""
    user_id = get_jwt_identity()
    
    if request.method == 'POST':
        data = request.json
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'error': 'Team name is required'}), 400

        slug = (data.get('slug') or '').strip()
        if not slug:
            base_slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') or 'team'
            slug = base_slug
            suffix = 1
            while Team.query.filter_by(slug=slug).first():
                suffix += 1
                slug = f"{base_slug}-{suffix}"

        team = Team(
            name=name,
            slug=slug,
            owner_id=user_id,
            description=data.get('description')
        )
        db.session.add(team)
        
        # Add owner to team
        user = User.query.get(user_id)
        team.members.append(user)
        
        db.session.commit()
        return jsonify({'team_id': team.id}), 201
    
    user = User.query.get(user_id)
    return jsonify({
        'teams': [{
            'id': t.id,
            'name': t.name,
            'slug': t.slug,
            'owner_id': t.owner_id,
            'member_count': len(t.members)
        } for t in user.teams]
    })

@teams_bp.route('/<int:team_id>/members', methods=['GET', 'POST'])
@jwt_required()
def team_members_route(team_id):
    """Manage team members"""
    user_id = get_jwt_identity()
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    if team.owner_id != user_id:
        return jsonify({'error': 'Only owner can manage members'}), 403
    
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        user_to_add = User.query.filter_by(username=username).first()
        
        if not user_to_add:
            return jsonify({'error': 'User not found'}), 404
        
        team.members.append(user_to_add)
        db.session.commit()
        return jsonify({'message': 'Member added'}), 201
    
    return jsonify({
        'members': [{
            'id': m.id,
            'username': m.username,
            'email': m.email
        } for m in team.members]
    })
