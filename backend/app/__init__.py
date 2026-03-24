from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///reposhield.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 900))
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.scan import scan_bp
    from app.routes.analytics import analytics_bp
    from app.routes.users import users_bp
    from app.routes.teams import teams_bp
    from app.routes.webhooks import webhooks_bp
    from app.routes.health import health_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(scan_bp, url_prefix='/api/scan')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(teams_bp, url_prefix='/api/teams')
    app.register_blueprint(webhooks_bp, url_prefix='/webhooks')
    app.register_blueprint(health_bp, url_prefix='/health')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
