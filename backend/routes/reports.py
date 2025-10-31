from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Video, Annotation, BestPractice, Review, User
from datetime import datetime
from collections import defaultdict

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@reports_bp.route('/video/<int:video_id>', methods=['GET'])
@jwt_required()
def generate_video_report(video_id):
    """Generate comprehensive report for a video"""
    try:
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # Get all annotations for this video
        annotations = Annotation.query.filter_by(video_id=video_id).all()
        
        # Calculate statistics
        total_annotations = len(annotations)
        
        # Group by category
        by_category = defaultdict(int)
        by_practice = defaultdict(int)
        by_status = defaultdict(int)
        by_type = defaultdict(int)
        
        positive_count = 0
        negative_count = 0
        
        for ann in annotations:
            by_category[ann.practice_category] += 1
            by_status[ann.status] += 1
            by_type[ann.annotation_type] += 1
            
            if ann.practice:
                by_practice[ann.practice.title] += 1
            
            # Check if it's a strength or improvement based on comment text
            if ann.comment:
                if '✅ STRENGTH' in ann.comment:
                    positive_count += 1
                elif '⚠️ IMPROVEMENT' in ann.comment:
                    negative_count += 1
        
        # Get best practices for this category
        if video.category:
            relevant_practices = BestPractice.query.filter_by(category=video.category).all()
            practices_found = len([ann for ann in annotations if ann.practice_id is not None])
            practices_coverage = (practices_found / len(relevant_practices) * 100) if relevant_practices else 0
        else:
            practices_coverage = 0
        
        # Build report
        report = {
            'video': video.to_dict(),
            'generated_at': datetime.utcnow().isoformat(),
            'summary': {
                'total_annotations': total_annotations,
                'positive_indicators': positive_count,
                'areas_for_improvement': negative_count,
                'practices_coverage_percent': round(practices_coverage, 2)
            },
            'breakdown': {
                'by_category': dict(by_category),
                'by_practice': dict(by_practice),
                'by_status': dict(by_status),
                'by_type': dict(by_type)
            },
            'annotations': [ann.to_dict() for ann in annotations],
            'strengths': [],
            'improvements': []
        }
        
        # Identify strengths and areas for improvement
        for ann in annotations:
            entry = {
                'practice': ann.practice.title if ann.practice else 'General',
                'timestamp': f"{int(ann.start_time)}s",
                'comment': ann.comment
            }
            
            # Check comment text to determine if it's a strength or improvement
            if ann.comment:
                if '✅ STRENGTH' in ann.comment:
                    report['strengths'].append(entry)
                elif '⚠️ IMPROVEMENT' in ann.comment:
                    report['improvements'].append(entry)
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/reviewer/<int:reviewer_id>', methods=['GET'])
@jwt_required()
def generate_reviewer_report(reviewer_id):
    """Generate report for a specific reviewer's activity"""
    try:
        user_id = int(get_jwt_identity())
        current_user = User.query.get(user_id)
        
        # Check permissions
        if current_user.role != 'admin' and user_id != reviewer_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        reviewer = User.query.get(reviewer_id)
        if not reviewer:
            return jsonify({'error': 'Reviewer not found'}), 404
        
        # Get reviewer's annotations
        annotations = Annotation.query.filter_by(reviewer_id=reviewer_id).all()
        videos_reviewed = len(set([ann.video_id for ann in annotations]))
        
        # Get reviews
        reviews = Review.query.filter_by(reviewer_id=reviewer_id).all()
        
        report = {
            'reviewer': reviewer.to_dict(),
            'generated_at': datetime.utcnow().isoformat(),
            'summary': {
                'total_annotations': len(annotations),
                'videos_reviewed': videos_reviewed,
                'reviews_in_progress': len([r for r in reviews if r.status == 'in_progress']),
                'reviews_completed': len([r for r in reviews if r.status == 'completed'])
            },
            'recent_activity': [
                {
                    'video_id': ann.video_id,
                    'video_title': ann.video.title if ann.video else 'Unknown',
                    'annotation_count': 1,
                    'date': ann.created_at.isoformat()
                }
                for ann in annotations[:10]  # Last 10 annotations
            ]
        }
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/summary', methods=['GET'])
@jwt_required()
def generate_system_summary():
    """Generate overall system summary report (admin only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build queries
        videos_query = Video.query
        annotations_query = Annotation.query
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            videos_query = videos_query.filter(Video.created_at >= start_dt)
            annotations_query = annotations_query.filter(Annotation.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            videos_query = videos_query.filter(Video.created_at <= end_dt)
            annotations_query = annotations_query.filter(Annotation.created_at <= end_dt)
        
        # Get counts
        total_videos = videos_query.count()
        total_annotations = annotations_query.count()
        analyzed_videos = videos_query.filter_by(is_analyzed=True).count()
        
        # Get category distribution
        videos = videos_query.all()
        category_distribution = defaultdict(int)
        for video in videos:
            if video.category:
                category_distribution[video.category] += 1
        
        # Get top reviewers
        reviewer_stats = db.session.query(
            User.id,
            User.email,
            User.first_name,
            User.last_name,
            db.func.count(Annotation.id).label('annotation_count')
        ).join(Annotation, User.id == Annotation.reviewer_id).group_by(User.id).order_by(db.func.count(Annotation.id).desc()).limit(5).all()
        
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'overview': {
                'total_videos': total_videos,
                'analyzed_videos': analyzed_videos,
                'total_annotations': total_annotations,
                'active_reviewers': len(reviewer_stats)
            },
            'videos_by_category': dict(category_distribution),
            'top_reviewers': [
                {
                    'id': r.id,
                    'email': r.email,
                    'name': f"{r.first_name} {r.last_name}",
                    'annotations': r.annotation_count
                }
                for r in reviewer_stats
            ]
        }
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/export/video/<int:video_id>', methods=['GET'])
@jwt_required()
def export_video_report(video_id):
    """Export video report as JSON"""
    try:
        # Get the report data
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        annotations = Annotation.query.filter_by(video_id=video_id).all()
        
        export_data = {
            'export_date': datetime.utcnow().isoformat(),
            'video': video.to_dict(),
            'annotations': [ann.to_dict() for ann in annotations],
            'total_annotations': len(annotations)
        }
        
        return jsonify(export_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

