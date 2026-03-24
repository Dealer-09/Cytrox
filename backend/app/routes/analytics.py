"""Analytics routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app import db
from app.models import User, Scan

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get user's analytics dashboard"""
    user_id = get_jwt_identity()
    
    # Total scans
    total_scans = Scan.query.filter_by(user_id=user_id).count()
    
    # Risk distribution
    risk_levels = db.session.query(
        Scan.risk_level,
        func.count(Scan.id)
    ).filter_by(user_id=user_id).group_by(Scan.risk_level).all()
    
    # Average risk score
    avg_score = db.session.query(func.avg(Scan.risk_score)).filter_by(
        user_id=user_id
    ).scalar() or 0
    
    # Languages analyzed (DB-agnostic)
    scans = Scan.query.filter_by(user_id=user_id).all()
    language_set = set()
    for scan in scans:
        if isinstance(scan.languages_detected, dict):
            language_set.update(scan.languages_detected.keys())
    
    return jsonify({
        'total_scans': total_scans,
        'average_risk_score': float(avg_score),
        'risk_distribution': {
            level: count for level, count in risk_levels
        },
        'languages_analyzed': sorted(language_set)
    })

@analytics_bp.route('/trends', methods=['GET'])
@jwt_required()
def get_trends():
    """Get scanning trends over time"""
    user_id = get_jwt_identity()
    days = request.args.get('days', 30, type=int)
    
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    scans_by_date = db.session.query(
        func.date(Scan.created_at).label('date'),
        func.count(Scan.id).label('count'),
        func.avg(Scan.risk_score).label('avg_score')
    ).filter(
        Scan.user_id == user_id,
        Scan.created_at >= datetime.utcnow() - timedelta(days=days)
    ).group_by(
        func.date(Scan.created_at)
    ).all()
    
    return jsonify({
        'trends': [{
            'date': str(record[0]),
            'scan_count': record[1],
            'average_risk_score': float(record[2]) if record[2] else 0
        } for record in scans_by_date]
    })

@analytics_bp.route('/top-findings', methods=['GET'])
@jwt_required()
def get_top_findings():
    """Get most common finding types"""
    user_id = get_jwt_identity()
    
    # This would require parsing the findings JSON
    # Simplified version
    scans = Scan.query.filter_by(user_id=user_id).all()
    
    finding_types = {}
    for scan in scans:
        if scan.findings and 'findings' in scan.findings:
            for finding in scan.findings['findings']:
                finding_type = finding.get('type', 'UNKNOWN')
                finding_types[finding_type] = finding_types.get(finding_type, 0) + 1
    
    sorted_findings = sorted(finding_types.items(), key=lambda x: x[1], reverse=True)
    
    return jsonify({
        'top_findings': [
            {'type': f_type, 'count': count}
            for f_type, count in sorted_findings[:10]
        ]
    })
