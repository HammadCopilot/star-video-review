from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, BestPractice

practices_bp = Blueprint('practices', __name__, url_prefix='/api/practices')


@practices_bp.route('', methods=['GET'])
@jwt_required()
def get_practices():
    """Get all best practices with optional filtering"""
    try:
        # Query parameters
        category = request.args.get('category')
        is_positive = request.args.get('is_positive')
        
        # Build query
        query = BestPractice.query
        
        if category:
            query = query.filter_by(category=category)
        if is_positive is not None:
            is_positive_bool = is_positive.lower() == 'true'
            query = query.filter_by(is_positive=is_positive_bool)
        
        # Order by category and order
        query = query.order_by(BestPractice.category, BestPractice.order)
        
        practices = query.all()
        
        return jsonify({
            'practices': [practice.to_dict() for practice in practices],
            'count': len(practices)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@practices_bp.route('/<int:practice_id>', methods=['GET'])
@jwt_required()
def get_practice(practice_id):
    """Get single best practice by ID"""
    try:
        practice = BestPractice.query.get(practice_id)
        
        if not practice:
            return jsonify({'error': 'Best practice not found'}), 404
        
        return jsonify({'practice': practice.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@practices_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all unique categories"""
    try:
        categories = db.session.query(BestPractice.category).distinct().all()
        category_list = [cat[0] for cat in categories]
        
        return jsonify({
            'categories': category_list,
            'count': len(category_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@practices_bp.route('/category/<string:category>', methods=['GET'])
@jwt_required()
def get_practices_by_category(category):
    """Get all practices for a specific category"""
    try:
        practices = BestPractice.query.filter_by(category=category).order_by(BestPractice.order).all()
        
        if not practices:
            return jsonify({'error': 'No practices found for this category'}), 404
        
        # Separate into positive and negative
        positive = [p.to_dict() for p in practices if p.is_positive]
        negative = [p.to_dict() for p in practices if not p.is_positive]
        
        return jsonify({
            'category': category,
            'positive_practices': positive,
            'negative_practices': negative,
            'total': len(practices)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

