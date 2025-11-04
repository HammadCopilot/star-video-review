from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config
from models import db
import os

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.videos import videos_bp
    from routes.annotations import annotations_bp
    from routes.practices import practices_bp
    from routes.ai_analysis import ai_bp
    from routes.reports import reports_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(videos_bp)
    app.register_blueprint(annotations_bp)
    app.register_blueprint(practices_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(reports_bp)

    # Serve React frontend in production
    if config_name == 'production':
        from flask import send_from_directory
        import os
        
        frontend_build_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'build')
        
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_frontend(path):
            if path.startswith('api/') or path == 'health':
                # API routes handled by blueprints above
                pass
            elif path != '' and os.path.exists(os.path.join(frontend_build_path, path)):
                return send_from_directory(frontend_build_path, path)
            else:
                return send_from_directory(frontend_build_path, 'index.html')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'STAR Video Review API'}), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'STAR Video Review API',
            'version': '2.0.0',
            'phase': 'Phase 2 - AI Integration',
            'endpoints': {
                'auth': '/api/auth',
                'videos': '/api/videos',
                'annotations': '/api/annotations',
                'practices': '/api/practices',
                'ai_analysis': '/api/ai',
                'reports': '/api/reports',
                'health': '/health'
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token', 'message': str(error)}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token is missing', 'message': str(error)}), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has been revoked'}), 401
    
    # Create database tables (handle race condition with multiple workers)
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            # Tables may already exist from another worker process
            print(f"Database initialization: {str(e)}")
            # Verify tables exist by attempting a simple query
            try:
                db.session.execute(db.text("SELECT 1"))
                print("Database tables already exist and are accessible.")
            except Exception as verify_error:
                print(f"Database verification failed: {str(verify_error)}")
                raise
    
    return app


if __name__ == '__main__':
    app = create_app()
    # Use port 5001 to avoid conflict with macOS AirPlay on port 5000
    app.run(host='0.0.0.0', port=5001, debug=True)

