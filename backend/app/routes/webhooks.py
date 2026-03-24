"""Webhook routes for CI/CD integration"""
from flask import Blueprint, request, jsonify, current_app
import hmac
import hashlib
import os
import asyncio
import threading
from app import db
from app.models import WebhookLog, Scan, User

webhooks_bp = Blueprint('webhooks', __name__)

def verify_github_webhook(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature"""
    secret = os.getenv('GITHUB_WEBHOOK_SECRET')
    if not secret or not signature:
        return False
    expected = 'sha256=' + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@webhooks_bp.route('/github', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook events"""
    payload = request.get_data()
    signature = request.headers.get('X-Hub-Signature-256', '')
    
    if not verify_github_webhook(payload, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    event_type = request.headers.get('X-GitHub-Event', '')
    data = request.json
    
    # Log webhook
    webhook_log = WebhookLog(
        event_type=event_type,
        provider='github',
        repository_url=data.get('repository', {}).get('html_url'),
        payload=data,
        status='RECEIVED'
    )
    db.session.add(webhook_log)
    db.session.commit()
    
    # Trigger scan for push events
    if event_type == 'push':
        repo_url = data.get('repository', {}).get('html_url')
        if repo_url:
            # Find user to associate scan with
            # In production, would use webhook authentication
            webhook_log.status = 'PROCESSING'
            db.session.commit()

            app_obj = current_app._get_current_object()
            threading.Thread(
                target=_run_webhook_scan_background,
                args=(app_obj, webhook_log.id, repo_url),
                daemon=True,
            ).start()
    
    return jsonify({'message': 'Webhook received'}), 200

@webhooks_bp.route('/gitlab', methods=['POST'])
def gitlab_webhook():
    """Handle GitLab webhook events"""
    token = request.headers.get('X-Gitlab-Token', '')
    secret = os.getenv('GITLAB_WEBHOOK_SECRET')

    if not secret or token != secret:
        return jsonify({'error': 'Invalid token'}), 401
    
    data = request.json
    event_type = request.headers.get('X-Gitlab-Event', '')
    
    webhook_log = WebhookLog(
        event_type=event_type,
        provider='gitlab',
        repository_url=data.get('project', {}).get('web_url'),
        payload=data,
        status='RECEIVED'
    )
    db.session.add(webhook_log)
    db.session.commit()
    
    if event_type == 'push':
        repo_url = data.get('project', {}).get('web_url')
        if repo_url:
            webhook_log.status = 'PROCESSING'
            db.session.commit()
            app_obj = current_app._get_current_object()
            threading.Thread(
                target=_run_webhook_scan_background,
                args=(app_obj, webhook_log.id, repo_url),
                daemon=True,
            ).start()
    
    return jsonify({'message': 'Webhook received'}), 200

def _run_webhook_scan_background(app, webhook_log_id: int, repo_url: str):
    """Background runner for webhook-triggered scans."""
    asyncio.run(_trigger_scan_from_webhook(app, webhook_log_id, repo_url))

async def _trigger_scan_from_webhook(app, webhook_log_id: int, repo_url: str):
    """Trigger scan from webhook event"""
    with app.app_context():
        # In production, would need to identify which user triggered this
        webhook_log = WebhookLog.query.get(webhook_log_id)
        if not webhook_log:
            return

        try:
            from app.routes.scan import _perform_scan

            # Create scan for webhook
            scan = Scan(
                user_id=1,  # Would be identified from webhook auth in production
                repository_url=repo_url,
                status='PENDING'
            )
            db.session.add(scan)
            db.session.commit()

            await _perform_scan(app, scan.id, repo_url)

            webhook_log.status = 'COMPLETED'
            webhook_log.scan_triggered = True
            webhook_log.scan_id = scan.id
            db.session.commit()

        except Exception:
            webhook_log.status = 'FAILED'
            db.session.commit()
