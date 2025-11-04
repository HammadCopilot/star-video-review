from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config
from models import db
import os

def create_app(config_name='development'):
    """Application factory"""
    # Disable Flask's default static file handling so we can serve the React build ourselves.
    # The default static handler responds to /static/* before our catch-all route, which caused
    # 404s because the static files live in ../frontend/build/static rather than backend/static.
    app = Flask(__name__, static_folder=None)
    
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

    # Health check endpoint (define before catch-all route)
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'STAR Video Review API'}), 200
    
    # API info endpoint (only for development)
    if config_name != 'production':
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

    # Serve React frontend in production (must be last route)
    if config_name == 'production':
        from flask import send_from_directory, make_response
        import os

        frontend_build_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'build')

        # Debug: Print frontend build path and verify it exists
        print(f"Frontend build path: {frontend_build_path}")
        print(f"Frontend build exists: {os.path.exists(frontend_build_path)}")
        if os.path.exists(frontend_build_path):
            print(f"Frontend build contents: {os.listdir(frontend_build_path)}")

        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_frontend(path):
            # Skip API routes - they're handled by blueprints
            if path.startswith('api/') or path.startswith('health'):
                # Return 404 if this route is reached (blueprint should handle it)
                return jsonify({'error': 'Not found'}), 404

            # If path is empty, serve index.html
            if path == '':
                response = make_response(send_from_directory(frontend_build_path, 'index.html'))
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response

            # Check if the requested file exists
            full_path = os.path.join(frontend_build_path, path)
            file_exists = os.path.exists(full_path) and os.path.isfile(full_path)
            
            if file_exists:
                # Serve static assets (JS, CSS, images, etc.) - these have content hashes so can be cached
                # The random characters (e.g., main.fa9bb86b.js) are content hashes for cache busting
                try:
                    response = make_response(send_from_directory(frontend_build_path, path))
                    # Cache static assets for 1 year since they have content hashes
                    response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
                    return response
                except Exception as e:
                    print(f"ERROR: Failed to serve file '{path}': {e}")
                    print(f"  Frontend build path: {frontend_build_path}")
                    print(f"  Requested path: {path}")
                    print(f"  Full path: {full_path}")
                    print(f"  File exists: {file_exists}")
                    # Fall through to serve index.html
            
            # File doesn't exist - serve index.html for client-side routing
            # This handles cases like:
            # - Old build artifacts referenced in cached HTML (browser requesting old hash filenames)
            # - Client-side routes that need to be handled by React Router
            response = make_response(send_from_directory(frontend_build_path, 'index.html'))
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
    
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

