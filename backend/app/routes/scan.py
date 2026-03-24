"""Scan routes"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import asyncio
import threading
import os
import tempfile
import shutil
from datetime import datetime
from git import Repo
from app import db
from app.models import User, Scan
from app.analyzers import MultiLanguageAnalyzer

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('/repository', methods=['POST'])
@jwt_required()
def scan_repository():
    """Scan a GitHub repository"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    repo_url = data.get('repository_url')
    
    if not repo_url:
        return jsonify({'error': 'Repository URL required'}), 400
    
    # Check subscription for private repos
    if 'private' in repo_url.lower() and user.subscription_tier == 'FREE':
        return jsonify({'error': 'Premium subscription required for private repos'}), 403
    
    # Create scan record
    scan = Scan(
        user_id=user_id,
        repository_url=repo_url,
        status='PENDING'
    )
    db.session.add(scan)
    db.session.commit()
    
    try:
        # Trigger scan in background thread to avoid request lifecycle cancellation.
        app_obj = current_app._get_current_object()
        threading.Thread(
            target=_run_scan_background,
            args=(app_obj, scan.id, repo_url),
            daemon=True,
        ).start()
        
        return jsonify({
            'scan_id': scan.id,
            'status': 'PENDING',
            'message': 'Scan queued successfully'
        }), 202
    
    except Exception as e:
        scan.status = 'FAILED'
        db.session.commit()
        return jsonify({'error': str(e)}), 500

def _run_scan_background(app, scan_id: int, repo_url: str):
    """Background runner for repository scans."""
    asyncio.run(_perform_scan(app, scan_id, repo_url))

@scan_bp.route('/<int:scan_id>', methods=['GET'])
@jwt_required()
def get_scan(scan_id):
    """Get scan results"""
    user_id = get_jwt_identity()
    scan = Scan.query.filter_by(id=scan_id, user_id=user_id).first()
    
    if not scan:
        return jsonify({'error': 'Scan not found'}), 404
    
    return jsonify({
        'id': scan.id,
        'repository_url': scan.repository_url,
        'status': scan.status,
        'risk_score': scan.risk_score,
        'risk_level': scan.risk_level,
        'findings': scan.findings,
        'summary': scan.summary,
        'scan_duration': scan.scan_duration,
        'created_at': scan.created_at.isoformat(),
        'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
    })

@scan_bp.route('/history', methods=['GET'])
@jwt_required()
def get_scan_history():
    """Get user's scan history"""
    user_id = get_jwt_identity()
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    scans = Scan.query.filter_by(user_id=user_id).order_by(
        Scan.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    return jsonify({
        'scans': [{
            'id': s.id,
            'repository_url': s.repository_url,
            'risk_level': s.risk_level,
            'risk_score': s.risk_score,
            'created_at': s.created_at.isoformat(),
            'status': s.status
        } for s in scans]
    })

async def _perform_scan(app, scan_id: int, repo_url: str):
    """Perform actual scan (runs asynchronously)"""
    with app.app_context():
        scan = Scan.query.get(scan_id)
        if not scan:
            return

        scan.status = 'RUNNING'
        db.session.commit()

        temp_dir = None
        try:
            # Clone repository
            temp_dir = tempfile.mkdtemp()
            start_time = datetime.utcnow()

            Repo.clone_from(repo_url, temp_dir, depth=1)

            # Run analysis
            analyzer = MultiLanguageAnalyzer()
            results = await analyzer.analyze_repository(temp_dir)

            # Calculate risk score
            risk_score = sum(50 if f['severity'] == 'CRITICAL' else
                            25 if f['severity'] == 'HIGH' else
                            10 if f['severity'] == 'MEDIUM' else
                            5 if f['severity'] == 'LOW' else 0
                            for f in results['findings'])

            # Determine risk level
            if risk_score >= 200:
                risk_level = 'CRITICAL'
            elif risk_score >= 100:
                risk_level = 'HIGH'
            elif risk_score >= 50:
                risk_level = 'MEDIUM'
            elif risk_score >= 20:
                risk_level = 'LOW'
            else:
                risk_level = 'SAFE'

            # Update scan
            end_time = datetime.utcnow()
            scan.status = 'COMPLETED'
            scan.risk_score = risk_score
            scan.risk_level = risk_level
            scan.findings = {'findings': results['findings']}
            scan.summary = {
                'total_files': results['total_files'],
                'analyzed_files': results['analyzed_files'],
                'languages_detected': results['languages_detected'],
                'critical_findings': len([f for f in results['findings'] if f['severity'] == 'CRITICAL']),
                'high_findings': len([f for f in results['findings'] if f['severity'] == 'HIGH']),
            }
            scan.scan_duration = int((end_time - start_time).total_seconds())
            scan.completed_at = end_time
            scan.total_files = results['total_files']
            scan.analyzed_files = results['analyzed_files']
            scan.languages_detected = results['languages_detected']

            db.session.commit()

        except Exception:
            scan.status = 'FAILED'
            db.session.commit()

        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
