from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSON, ENUM
import enum

class SeverityEnum(enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar_url = db.Column(db.String(255))
    
    # Subscription
    subscription_tier = db.Column(db.String(50), default='FREE')  # FREE, PRO, ENTERPRISE
    subscription_active = db.Column(db.Boolean, default=False)
    subscription_expires = db.Column(db.DateTime)
    
    # Account
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    scans = db.relationship('Scan', backref='user', lazy=True, cascade='all, delete-orphan')
    teams = db.relationship('Team', secondary='team_members', backref='members')
    payments = db.relationship('Payment', backref='user', lazy=True, cascade='all, delete-orphan')
    
class Team(db.Model):
    """Team model for collaboration"""
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = db.relationship('User', backref='owned_teams')
    scans = db.relationship('Scan', backref='team', lazy=True)

class Scan(db.Model):
    """Scan results storage"""
    __tablename__ = 'scans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    
    repository_url = db.Column(db.String(255), nullable=False)
    repository_owner = db.Column(db.String(100))
    repository_name = db.Column(db.String(100))
    
    status = db.Column(db.String(50), default='PENDING')  # PENDING, RUNNING, COMPLETED, FAILED
    risk_score = db.Column(db.Integer, default=0)
    risk_level = db.Column(db.String(50))  # SAFE, LOW, MEDIUM, HIGH, CRITICAL
    
    findings = db.Column(JSON, default={})
    summary = db.Column(JSON, default={})
    
    scan_duration = db.Column(db.Integer)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Analysis details
    total_files = db.Column(db.Integer)
    analyzed_files = db.Column(db.Integer)
    languages_detected = db.Column(JSON, default={})

class Finding(db.Model):
    """Individual security findings"""
    __tablename__ = 'findings'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    
    type = db.Column(db.String(100))  # DANGEROUS_CALL, SECRET, OBFUSCATION, etc.
    severity = db.Column(ENUM(SeverityEnum), default=SeverityEnum.INFO)
    
    file_path = db.Column(db.String(255))
    line_number = db.Column(db.Integer)
    code_snippet = db.Column(db.Text)
    
    message = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    why_it_matters = db.Column(db.Text)
    
    confidence = db.Column(db.Float, default=1.0)  # 0.0 - 1.0
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    scan = db.relationship('Scan', backref='findings_list')

class Payment(db.Model):
    """Payment history for subscriptions"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    stripe_id = db.Column(db.String(100), unique=True)
    amount = db.Column(db.Float)
    currency = db.Column(db.String(10), default='USD')
    
    plan = db.Column(db.String(50))  # PRO, ENTERPRISE
    status = db.Column(db.String(50), default='PENDING')  # PENDING, COMPLETED, FAILED
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

class WebhookLog(db.Model):
    """Webhook delivery logs"""
    __tablename__ = 'webhook_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100))  # push, pull_request, schedule, etc.
    provider = db.Column(db.String(50))  # github, gitlab, jenkins
    
    repository_url = db.Column(db.String(255))
    payload = db.Column(JSON)
    
    status = db.Column(db.String(50))  # RECEIVED, PROCESSING, COMPLETED
    scan_triggered = db.Column(db.Boolean, default=False)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Association table for team members
team_members = db.Table('team_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('teams.id'), primary_key=True)
)
