import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    # Disable CSRF for API usage (since we're not using cookies)
    JWT_COOKIE_CSRF_PROTECT = False
    
    # Database
    # Default to SQLite for development, but support PostgreSQL for production
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///star_video_review.db')
    
    # Handle PostgreSQL SSL requirements for Neon
    if DATABASE_URL.startswith('postgresql://'):
        # Check if psycopg2 is available before using PostgreSQL
        try:
            import psycopg2
            # Neon requires SSL connections
            if 'sslmode=' not in DATABASE_URL:
                DATABASE_URL += '?sslmode=require'
        except ImportError:
            print("WARNING: psycopg2 not available, falling back to SQLite")
            DATABASE_URL = 'sqlite:///star_video_review.db'
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # PostgreSQL connection pool settings (only used when using PostgreSQL)
    if SQLALCHEMY_DATABASE_URI.startswith('postgresql://'):
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 10,
            'pool_recycle': 120,
            'pool_pre_ping': True,
            'max_overflow': 20
        }
    
    # File Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 2 * 1024 * 1024 * 1024))  # 2GB default
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # AI Settings
    USE_ENHANCED_AI = os.getenv('USE_ENHANCED_AI', 'True').lower() == 'true'  # Default to True
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'small')
    WHISPER_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    
    # CORS
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    @staticmethod
    def init_app(app):
        """Initialize application"""
        # Create upload folder if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.WHISPER_MODEL_PATH, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

