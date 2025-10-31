from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db, Video, User, AuditLog
from datetime import datetime
import os
import requests
import json

# Import moviepy only when needed (optional dependency)
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    VideoFileClip = None

videos_bp = Blueprint('videos', __name__, url_prefix='/api/videos')


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_VIDEO_EXTENSIONS']


def get_video_duration(file_path):
    """Get video duration in seconds"""
    if not MOVIEPY_AVAILABLE:
        print("MoviePy not available, skipping duration extraction")
        return None
    
    try:
        clip = VideoFileClip(file_path)
        duration = clip.duration
        clip.close()
        return duration
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return None


@videos_bp.route('', methods=['GET'])
@jwt_required()
def get_videos():
    """Get all videos with optional filtering"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Query parameters
        category = request.args.get('category')
        status = request.args.get('status')
        uploader_id = request.args.get('uploader_id')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Video.query
        
        if category:
            query = query.filter_by(category=category)
        if status:
            query = query.filter_by(analysis_status=status)
        if uploader_id:
            query = query.filter_by(uploader_id=uploader_id)
        
        # Order by created_at desc
        query = query.order_by(Video.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'videos': [video.to_dict() for video in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@videos_bp.route('/<int:video_id>', methods=['GET'])
@jwt_required()
def get_video(video_id):
    """Get single video by ID"""
    try:
        user_id = int(get_jwt_identity())
        video = Video.query.get(video_id)
        
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # Create audit log
        audit = AuditLog(
            user_id=user_id,
            action='video_viewed',
            resource_type='video',
            resource_id=video_id,
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
        
        return jsonify({'video': video.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@videos_bp.route('', methods=['POST'])
@jwt_required()
def create_video():
    """Upload video (local file) or add external URL"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Check if it's a file upload or URL
        if 'file' in request.files:
            # Local file upload
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'File type not allowed'}), 400
            
            # Secure filename and save
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            file.save(file_path)
            
            # Get video duration
            duration = get_video_duration(file_path)
            
            # Create video record
            video = Video(
                title=request.form.get('title', filename),
                description=request.form.get('description'),
                source_type='local',
                file_path=filename,
                uploader_id=user_id,
                duration=duration,
                category=request.form.get('category')
            )
            
        else:
            # External URL
            data = request.get_json()
            
            if 'url' not in data:
                return jsonify({'error': 'URL is required'}), 400
            
            video = Video(
                title=data.get('title', 'Untitled Video'),
                description=data.get('description'),
                source_type='url',
                url=data['url'],
                uploader_id=user_id,
                category=data.get('category')
            )
        
        db.session.add(video)
        db.session.commit()
        
        # Create audit log
        audit = AuditLog(
            user_id=user_id,
            action='video_uploaded',
            resource_type='video',
            resource_id=video.id,
            details=json.dumps({'source_type': video.source_type}),
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
        
        return jsonify({
            'message': 'Video created successfully',
            'video': video.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@videos_bp.route('/<int:video_id>', methods=['PUT'])
@jwt_required()
def update_video(video_id):
    """Update video metadata"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        video = Video.query.get(video_id)
        
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # Check permissions
        if user.role not in ['admin', 'reviewer'] and video.uploader_id != user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        
        # Update allowed fields
        if 'title' in data:
            video.title = data['title']
        if 'description' in data:
            video.description = data['description']
        if 'category' in data:
            video.category = data['category']
        
        video.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Video updated successfully',
            'video': video.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@videos_bp.route('/<int:video_id>', methods=['DELETE'])
@jwt_required()
def delete_video(video_id):
    """Delete video"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        video = Video.query.get(video_id)
        
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # Check permissions (admin or owner)
        if user.role != 'admin' and video.uploader_id != user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # Delete physical file if local
        if video.source_type == 'local' and video.file_path:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], video.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(video)
        db.session.commit()
        
        return jsonify({'message': 'Video deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@videos_bp.route('/<int:video_id>/stream', methods=['GET'])
@jwt_required(optional=True)
def stream_video(video_id):
    """Stream video file with range support for seeking"""
    try:
        # Check authentication - either via header or query param
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        
        try:
            # Try to verify JWT from header first
            verify_jwt_in_request()
        except:
            # If header auth fails, try query parameter
            token = request.args.get('token')
            if not token:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Verify token from query parameter
            from flask_jwt_extended import decode_token
            try:
                decode_token(token)
            except:
                return jsonify({'error': 'Invalid token'}), 401
        
        video = Video.query.get(video_id)
        
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        if video.source_type == 'url':
            return jsonify({'error': 'External URL videos cannot be streamed', 'url': video.url}), 400
        
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], video.file_path)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Video file not found'}), 404
        
        # Determine MIME type based on file extension
        file_ext = video.file_path.rsplit('.', 1)[-1].lower()
        mime_types = {
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'mkv': 'video/x-matroska',
            'webm': 'video/webm',
            'flv': 'video/x-flv'
        }
        mime_type = mime_types.get(file_ext, 'video/mp4')
        
        return send_file(
            file_path, 
            mimetype=mime_type,
            as_attachment=False,
            conditional=True  # Enable range requests for seeking
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

