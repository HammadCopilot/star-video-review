from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Annotation, Video, User, BestPractice
from datetime import datetime

annotations_bp = Blueprint('annotations', __name__, url_prefix='/api/annotations')


@annotations_bp.route('', methods=['POST'])
@jwt_required()
def create_annotation():
    """Create a new annotation"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['video_id', 'start_time', 'practice_category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify video exists
        video = Video.query.get(data['video_id'])
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # Create annotation
        annotation = Annotation(
            video_id=data['video_id'],
            reviewer_id=user_id,
            start_time=data['start_time'],
            end_time=data.get('end_time'),
            practice_category=data['practice_category'],
            practice_id=data.get('practice_id'),
            comment=data.get('comment'),
            annotation_type=data.get('annotation_type', 'manual'),
            status=data.get('status', 'approved'),
            confidence_score=data.get('confidence_score')
        )
        
        db.session.add(annotation)
        db.session.commit()
        
        return jsonify({
            'message': 'Annotation created successfully',
            'annotation': annotation.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@annotations_bp.route('', methods=['GET'])
@jwt_required()
def get_annotations():
    """Get annotations with optional filtering"""
    try:
        # Query parameters
        video_id = request.args.get('video_id', type=int)
        reviewer_id = request.args.get('reviewer_id', type=int)
        practice_category = request.args.get('practice_category')
        status = request.args.get('status')
        annotation_type = request.args.get('annotation_type')
        
        # Build query
        query = Annotation.query
        
        if video_id:
            query = query.filter_by(video_id=video_id)
        if reviewer_id:
            query = query.filter_by(reviewer_id=reviewer_id)
        if practice_category:
            query = query.filter_by(practice_category=practice_category)
        if status:
            query = query.filter_by(status=status)
        if annotation_type:
            query = query.filter_by(annotation_type=annotation_type)
        
        # Order by video_id and start_time
        query = query.order_by(Annotation.video_id, Annotation.start_time)
        
        annotations = query.all()
        
        return jsonify({
            'annotations': [ann.to_dict() for ann in annotations],
            'count': len(annotations)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@annotations_bp.route('/<int:annotation_id>', methods=['GET'])
@jwt_required()
def get_annotation(annotation_id):
    """Get single annotation by ID"""
    try:
        annotation = Annotation.query.get(annotation_id)
        
        if not annotation:
            return jsonify({'error': 'Annotation not found'}), 404
        
        return jsonify({'annotation': annotation.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@annotations_bp.route('/<int:annotation_id>', methods=['PUT'])
@jwt_required()
def update_annotation(annotation_id):
    """Update annotation"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        annotation = Annotation.query.get(annotation_id)
        
        if not annotation:
            return jsonify({'error': 'Annotation not found'}), 404
        
        # Check permissions (owner or admin)
        if user.role != 'admin' and annotation.reviewer_id != user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        
        # Update allowed fields
        if 'start_time' in data:
            annotation.start_time = data['start_time']
        if 'end_time' in data:
            annotation.end_time = data['end_time']
        if 'practice_category' in data:
            annotation.practice_category = data['practice_category']
        if 'practice_id' in data:
            annotation.practice_id = data['practice_id']
        if 'comment' in data:
            annotation.comment = data['comment']
        if 'status' in data:
            annotation.status = data['status']
        if 'confidence_score' in data:
            annotation.confidence_score = data['confidence_score']
        
        annotation.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Annotation updated successfully',
            'annotation': annotation.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@annotations_bp.route('/<int:annotation_id>', methods=['DELETE'])
@jwt_required()
def delete_annotation(annotation_id):
    """Delete annotation"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        annotation = Annotation.query.get(annotation_id)
        
        if not annotation:
            return jsonify({'error': 'Annotation not found'}), 404
        
        # Check permissions (owner or admin)
        if user.role != 'admin' and annotation.reviewer_id != user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        db.session.delete(annotation)
        db.session.commit()
        
        return jsonify({'message': 'Annotation deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@annotations_bp.route('/video/<int:video_id>/summary', methods=['GET'])
@jwt_required()
def get_video_annotation_summary(video_id):
    """Get annotation summary for a video"""
    try:
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        annotations = Annotation.query.filter_by(video_id=video_id).all()
        
        # Calculate summary statistics
        total_annotations = len(annotations)
        by_category = {}
        by_status = {}
        by_type = {}
        
        for ann in annotations:
            # By category
            category = ann.practice_category
            if category not in by_category:
                by_category[category] = 0
            by_category[category] += 1
            
            # By status
            status = ann.status
            if status not in by_status:
                by_status[status] = 0
            by_status[status] += 1
            
            # By type
            ann_type = ann.annotation_type
            if ann_type not in by_type:
                by_type[ann_type] = 0
            by_type[ann_type] += 1
        
        return jsonify({
            'video_id': video_id,
            'video_title': video.title,
            'summary': {
                'total_annotations': total_annotations,
                'by_category': by_category,
                'by_status': by_status,
                'by_type': by_type
            },
            'annotations': [ann.to_dict() for ann in annotations]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@annotations_bp.route('/bulk', methods=['POST'])
@jwt_required()
def create_bulk_annotations():
    """Create multiple annotations at once (for AI-generated annotations)"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if 'annotations' not in data or not isinstance(data['annotations'], list):
            return jsonify({'error': 'annotations array is required'}), 400
        
        created_annotations = []
        
        for ann_data in data['annotations']:
            # Validate required fields
            if 'video_id' not in ann_data or 'start_time' not in ann_data or 'practice_category' not in ann_data:
                continue
            
            annotation = Annotation(
                video_id=ann_data['video_id'],
                reviewer_id=user_id,
                start_time=ann_data['start_time'],
                end_time=ann_data.get('end_time'),
                practice_category=ann_data['practice_category'],
                practice_id=ann_data.get('practice_id'),
                comment=ann_data.get('comment'),
                annotation_type=ann_data.get('annotation_type', 'ai_generated'),
                status=ann_data.get('status', 'draft'),
                confidence_score=ann_data.get('confidence_score')
            )
            
            db.session.add(annotation)
            created_annotations.append(annotation)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(created_annotations)} annotations created successfully',
            'annotations': [ann.to_dict() for ann in created_annotations]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

