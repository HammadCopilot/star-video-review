from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='reviewer')  # admin, reviewer, viewer
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    videos = db.relationship('Video', backref='uploader', lazy='dynamic', foreign_keys='Video.uploader_id')
    annotations = db.relationship('Annotation', backref='reviewer', lazy='dynamic')
    reviews = db.relationship('Review', backref='reviewer', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Video(db.Model):
    """Video model for storing video metadata"""
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    source_type = db.Column(db.String(20), nullable=False)  # 'local' or 'url'
    file_path = db.Column(db.String(500))  # For local files
    url = db.Column(db.String(500))  # For external URLs
    duration = db.Column(db.Float)  # Duration in seconds
    thumbnail_path = db.Column(db.String(500))
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50))  # discrete_trial, pivotal_response, functional_routines
    is_analyzed = db.Column(db.Boolean, default=False)
    analysis_status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    annotations = db.relationship('Annotation', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    transcripts = db.relationship('Transcript', backref='video', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'source_type': self.source_type,
            'file_path': self.file_path,
            'url': self.url,
            'duration': self.duration,
            'thumbnail_path': self.thumbnail_path,
            'uploader_id': self.uploader_id,
            'uploader': self.uploader.to_dict() if self.uploader else None,
            'category': self.category,
            'is_analyzed': self.is_analyzed,
            'analysis_status': self.analysis_status,
            'annotation_count': self.annotations.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Annotation(db.Model):
    """Annotation model for timestamped tags and comments"""
    __tablename__ = 'annotations'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.Float, nullable=False)  # Start time in seconds
    end_time = db.Column(db.Float)  # End time in seconds (optional)
    practice_category = db.Column(db.String(50), nullable=False)  # discrete_trial, pivotal_response, functional_routines
    practice_id = db.Column(db.Integer, db.ForeignKey('best_practices.id'))
    comment = db.Column(db.Text)
    annotation_type = db.Column(db.String(20), default='manual')  # manual, ai_generated
    status = db.Column(db.String(20), default='approved')  # draft, approved, rejected
    confidence_score = db.Column(db.Float)  # For AI-generated annotations
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    practice = db.relationship('BestPractice', backref='annotations')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'video_id': self.video_id,
            'reviewer_id': self.reviewer_id,
            'reviewer': self.reviewer.to_dict() if self.reviewer else None,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'practice_category': self.practice_category,
            'practice_id': self.practice_id,
            'practice': self.practice.to_dict() if self.practice else None,
            'comment': self.comment,
            'annotation_type': self.annotation_type,
            'status': self.status,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class BestPractice(db.Model):
    """Best practice criteria for annotations"""
    __tablename__ = 'best_practices'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # discrete_trial, pivotal_response, functional_routines
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    criteria = db.Column(db.Text)  # Detailed criteria/checklist
    is_positive = db.Column(db.Boolean, default=True)  # True for strengths, False for areas of improvement
    order = db.Column(db.Integer, default=0)  # Display order
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'criteria': self.criteria,
            'is_positive': self.is_positive,
            'order': self.order
        }


class Review(db.Model):
    """Review model to track video review status"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, archived
    notes = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'video_id': self.video_id,
            'reviewer_id': self.reviewer_id,
            'reviewer': self.reviewer.to_dict() if self.reviewer else None,
            'status': self.status,
            'notes': self.notes,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Transcript(db.Model):
    """Transcript model for storing video transcriptions"""
    __tablename__ = 'transcripts'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    method = db.Column(db.String(20), nullable=False)  # 'local_whisper' or 'openai_api'
    language = db.Column(db.String(10), default='en')
    confidence = db.Column(db.Float)
    processing_time = db.Column(db.Float)  # Time in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'video_id': self.video_id,
            'content': self.content,
            'method': self.method,
            'language': self.language,
            'confidence': self.confidence,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(db.Model):
    """Audit log for tracking user actions and API calls"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False)  # video_viewed, video_uploaded, ai_analysis, etc.
    resource_type = db.Column(db.String(50))  # video, annotation, user, etc.
    resource_id = db.Column(db.Integer)
    details = db.Column(db.Text)  # JSON string with additional details
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

