from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Video, Annotation, BestPractice, Transcript, AuditLog
from services.ai_analyzer import AIAnalyzer
from datetime import datetime
import os
import json
import requests
from urllib.parse import urlparse

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/analyze/<int:video_id>', methods=['POST'])
@jwt_required()
def analyze_video(video_id):
    """
    Analyze video with AI
    
    Request body (optional):
    {
        "use_enhanced": true/false,  # Override default setting
        "generate_annotations": true/false  # Auto-create annotations from results
    }
    """
    try:
        user_id = int(get_jwt_identity())
        video = Video.query.get(video_id)
        
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # Get request options
        data = request.get_json() or {}
        use_enhanced = data.get('use_enhanced', current_app.config.get('USE_ENHANCED_AI', True))  # Default to True
        generate_annotations = data.get('generate_annotations', True)
        
        # Handle URL videos - download them first
        if video.source_type == 'url':
            try:
                # Generate filename
                parsed_url = urlparse(video.url)
                path_parts = parsed_url.path.split('.')
                extension = path_parts[-1] if len(path_parts) > 1 and len(path_parts[-1]) <= 4 else 'mp4'
                
                # Clean title for filename
                safe_title = "".join(c for c in video.title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title.replace(' ', '_')[:50]
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{safe_title}.{extension}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                
                # Download video
                print(f"Downloading video from URL: {video.url}")
                response = requests.get(video.url, stream=True, timeout=60)
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"Downloaded video to: {file_path}")
                
                # Extract video duration
                try:
                    import cv2
                    cap = cv2.VideoCapture(file_path)
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    duration = frame_count / fps if fps > 0 else None
                    cap.release()
                    print(f"✅ Extracted duration: {duration}s")
                except Exception as e:
                    print(f"⚠️ Could not extract duration: {e}")
                    duration = None
                
                # Update video to local file but keep original URL
                original_url = video.url  # Preserve original URL
                video.source_type = 'local'
                video.file_path = filename
                video.duration = duration
                # Keep original URL in a new field or description
                if original_url and not video.description:
                    video.description = f"Downloaded from: {original_url}"
                elif original_url and original_url not in video.description:
                    video.description = f"{video.description}\nOriginal URL: {original_url}"
                # Keep original URL for reference
                video.video_metadata = json.dumps({'original_url': original_url, 'progress': 10, 'stage': 'Video downloaded, starting analysis...'})
                # Don't clear the URL completely, keep it for reference
                # video.url = None
                db.session.commit()
                
                video_file = file_path
                
            except Exception as e:
                return jsonify({
                    'error': 'Failed to download video from URL',
                    'message': str(e)
                }), 500
        else:
            # Get local video file path
            video_file = os.path.join(current_app.config['UPLOAD_FOLDER'], video.file_path)
        
        if not os.path.exists(video_file):
            return jsonify({'error': 'Video file not found on server'}), 404
        
        # Extract duration if not already present (for older videos)
        if not video.duration:
            try:
                import cv2
                cap = cv2.VideoCapture(video_file)
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = frame_count / fps if fps > 0 else None
                cap.release()
                if duration:
                    video.duration = duration
                    db.session.commit()
                    print(f"✅ Extracted missing duration: {duration}s")
            except Exception as e:
                print(f"⚠️ Could not extract duration: {e}")
        
        # Get best practices for analysis
        best_practices = BestPractice.query.all()
        practices_list = [p.to_dict() for p in best_practices]
        
        # Initialize AI analyzer
        api_key = current_app.config.get('OPENAI_API_KEY')
        analyzer = AIAnalyzer(api_key=api_key, use_enhanced=use_enhanced)
        
        # Update video status with initial progress
        video.analysis_status = 'processing'
        initial_metadata = {'progress': 5, 'stage': 'Initializing AI analysis...'}
        video.video_metadata = json.dumps(initial_metadata)
        db.session.commit()
        print(f"🚀 Started analysis for video {video_id}, initial metadata: {initial_metadata}")
        
        # Run analysis
        try:
            # Update progress: Transcription starting
            video.video_metadata = json.dumps({'progress': 15, 'stage': 'Transcribing audio with Whisper...'})
            db.session.commit()
            
            # Small delay to ensure progress is visible
            import time
            time.sleep(0.5)
            
            # Run analysis with progress updates
            results = analyzer.analyze_video(
                video_file,
                practices_list,
                video.category,
                use_enhanced
            )
            
            # Update progress after analysis
            if results.get('frames_extracted', 0) > 0:
                video.video_metadata = json.dumps({'progress': 85, 'stage': f"Analyzed audio + {results['frames_extracted']} video frames"})
            else:
                video.video_metadata = json.dumps({'progress': 85, 'stage': 'Audio analysis complete'})
            db.session.commit()
            
            # Update progress: Saving results
            video.video_metadata = json.dumps({'progress': 90, 'stage': 'Generating annotations...'})
            db.session.commit()
            
            # Save transcript if available
            if 'transcript' in results:
                transcript_data = results['transcript']
                
                # Check if transcript already exists
                existing_transcript = Transcript.query.filter_by(video_id=video_id).first()
                if existing_transcript:
                    # Update existing
                    existing_transcript.content = transcript_data['text']
                    existing_transcript.method = transcript_data['method']
                    existing_transcript.processing_time = transcript_data.get('processing_time')
                else:
                    # Create new
                    transcript = Transcript(
                        video_id=video_id,
                        content=transcript_data['text'],
                        method=transcript_data['method'],
                        language=transcript_data.get('language', 'en'),
                        processing_time=transcript_data.get('processing_time')
                    )
                    db.session.add(transcript)
            
            # Delete old AI-generated annotations on re-analysis
            old_annotations = Annotation.query.filter_by(
                video_id=video_id,
                annotation_type='ai_generated'
            ).all()
            if old_annotations:
                print(f"Deleting {len(old_annotations)} old AI annotations before re-analysis...")
                for old_ann in old_annotations:
                    db.session.delete(old_ann)
                db.session.commit()
            
            # Create annotations if requested
            created_annotations = []
            if generate_annotations and 'annotations' in results:
                # Get transcript segments for timestamp mapping
                transcript_data = results.get('transcript', {})
                segments = transcript_data.get('segments', [])
                print(f"🔍 DEBUG: Found {len(segments)} transcript segments for timestamp mapping")
                
                for ann_index, ann_data in enumerate(results['annotations']):
                    # Find matching best practice
                    practice = BestPractice.query.filter_by(title=ann_data.get('practice_title')).first()
                    
                    # Determine if this is a strength or improvement
                    is_positive = ann_data.get('is_positive', False)
                    
                    # Handle both transcript annotations (with 'comment') and visual annotations (with 'description')
                    comment_text = ann_data.get('comment') or ann_data.get('description', '')
                    
                    # Add strength/improvement indicator
                    if is_positive:
                        comment_text = f"✅ STRENGTH: {comment_text}"
                    else:
                        comment_text = f"⚠️ IMPROVEMENT NEEDED: {comment_text}"
                    
                    # Add quote if available (from transcript analysis)
                    if ann_data.get('quote'):
                        comment_text = f"{comment_text}\n\nQuote: \"{ann_data.get('quote')}\""
                    
                    # Add frame numbers if available (from visual analysis)
                    if ann_data.get('frame_numbers'):
                        comment_text = f"{comment_text}\n\nObserved in: {ann_data.get('frame_numbers')}"
                    
                    # Estimate timestamp: distribute annotations evenly across video duration
                    start_time = 0.0
                    quote = ann_data.get('quote', '').strip()
                    
                    # Skip matching for N/A quotes (from visual analysis) or empty quotes
                    if segments and quote and quote.lower() not in ['n/a', 'na', 'none', '']:
                        # Try to find matching segment by quote
                        quote_search = quote[:100]  # Use more characters for better matching
                        print(f"🔍 Matching quote: '{quote_search[:50]}...'")
                        
                        for seg in segments:
                            # Handle both dict and object formats
                            if hasattr(seg, 'text'):
                                seg_text = getattr(seg, 'text', '').strip()
                                seg_start = getattr(seg, 'start', 0)
                            else:
                                seg_text = seg.get('text', '').strip()
                                seg_start = seg.get('start', 0)
                            
                            # Try matching with the quote
                            if quote_search.lower() in seg_text.lower():
                                start_time = float(seg_start)
                                print(f"✅ Found match at {start_time}s: '{seg_text[:50]}'")
                                break
                        
                        if start_time == 0.0:
                            print(f"⚠️ No match found for quote, using distribution")
                    
                    # If no match or no quote, distribute evenly
                    if start_time == 0.0 and video.duration:
                        # Distribute evenly across video duration
                        total_annotations = len(results['annotations'])
                        start_time = (ann_index / max(1, total_annotations - 1)) * video.duration if total_annotations > 1 else 0
                        print(f"📍 Distributed timestamp for annotation {ann_index+1}/{total_annotations}: {start_time}s")
                    
                    annotation = Annotation(
                        video_id=video_id,
                        reviewer_id=user_id,
                        start_time=round(start_time, 1),  # Round to 1 decimal place
                        practice_category=video.category or 'general',
                        practice_id=practice.id if practice else None,
                        comment=comment_text,
                        annotation_type='ai_generated',
                        status='draft' if is_positive else 'needs_review',  # Flag improvements for review
                        confidence_score=ann_data.get('confidence', 0.0)
                    )
                    db.session.add(annotation)
                    created_annotations.append(annotation)
            
            # Update video status
            video.is_analyzed = True
            video.analysis_status = 'completed'
            video.video_metadata = json.dumps({'progress': 100, 'stage': 'Complete!'})
            db.session.commit()
            
            # Create audit log
            audit = AuditLog(
                user_id=user_id,
                action='ai_analysis',
                resource_type='video',
                resource_id=video_id,
                details=json.dumps({
                    'method': results.get('method'),
                    'use_enhanced': use_enhanced,
                    'annotations_created': len(created_annotations)
                }),
                ip_address=request.remote_addr
            )
            db.session.add(audit)
            db.session.commit()
            
            return jsonify({
                'message': 'Video analysis completed successfully',
                'results': {
                    'video_id': video_id,
                    'method': results.get('method'),
                    'transcript_length': len(results.get('transcript', {}).get('text', '')),
                    'processing_time': results.get('transcript', {}).get('processing_time'),
                    'frames_extracted': results.get('frames_extracted', 0),
                    'annotations_created': len(created_annotations),
                    'status': 'completed'
                },
                'transcript': results.get('transcript', {}).get('text', '')[:500] + '...',  # First 500 chars
                'annotations': [ann.to_dict() for ann in created_annotations]
            }), 200
            
        except Exception as analysis_error:
            # Update video status on error
            video.analysis_status = 'failed'
            db.session.commit()
            raise analysis_error
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/transcript/<int:video_id>', methods=['GET'])
@jwt_required()
def get_transcript(video_id):
    """Get transcript for a video"""
    try:
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        transcript = Transcript.query.filter_by(video_id=video_id).first()
        if not transcript:
            return jsonify({'error': 'Transcript not found. Run AI analysis first.'}), 404
        
        return jsonify({
            'transcript': transcript.to_dict(),
            'video': {
                'id': video.id,
                'title': video.title,
                'duration': video.duration
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/status/<int:video_id>', methods=['GET'])
@jwt_required()
def get_analysis_status(video_id):
    """Get AI analysis status and progress for a video"""
    try:
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        transcript = Transcript.query.filter_by(video_id=video_id).first()
        annotations = Annotation.query.filter_by(
            video_id=video_id,
            annotation_type='ai_generated'
        ).count()
        
        # Parse progress from metadata
        progress_data = {'progress': 0, 'stage': 'Not started'}
        if video.video_metadata:
            try:
                metadata = json.loads(video.video_metadata)
                if 'progress' in metadata:
                    progress_data = {
                        'progress': metadata.get('progress', 0),
                        'stage': metadata.get('stage', 'Processing...')
                    }
            except:
                pass
        
        return jsonify({
            'video_id': video_id,
            'is_analyzed': video.is_analyzed,
            'analysis_status': video.analysis_status,
            'progress': progress_data['progress'],
            'stage': progress_data['stage'],
            'has_transcript': transcript is not None,
            'ai_annotations_count': annotations
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

