"""
YouTube Video Downloader using yt-dlp
Handles YouTube videos, including Shorts, for AI analysis
"""

import os
import yt_dlp
from app import create_app
from models import db, Video
from datetime import datetime
import cv2

def download_youtube_video(url, title=None, category=None, uploader_id=1):
    """
    Download a YouTube video and add it to the database
    
    Args:
        url: YouTube video URL
        title: Optional custom title
        category: Video category (discrete_trial, pivotal_response, functional_routines)
        uploader_id: User ID who is adding the video
    """
    app = create_app()
    
    with app.app_context():
        uploads_dir = app.config['UPLOAD_FOLDER']
        
        # Create uploads directory if it doesn't exist
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Configure yt-dlp options
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        ydl_opts = {
            'format': 'best[height<=720][ext=mp4]/best[height<=720]/best[ext=mp4]/best',  # Prefer mp4 up to 720p
            'outtmpl': os.path.join(uploads_dir, f'{timestamp}_%(title)s.%(ext)s'),
            'restrictfilenames': True,  # Use only ASCII characters in filenames
            'noplaylist': True,  # Only download single video, not playlist
            'merge_output_format': 'mp4',  # Ensure final output is mp4
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video info first
                print(f"📹 Extracting video info from: {url}")
                info = ydl.extract_info(url, download=False)
                
                video_title = title or info.get('title', 'YouTube Video')
                duration = info.get('duration', 0)
                
                print(f"📋 Title: {video_title}")
                print(f"⏱️  Duration: {duration}s")
                
                # Download the video
                print(f"⬇️  Downloading video...")
                ydl.download([url])
                
                # Find the downloaded file
                expected_filename = ydl.prepare_filename(info)
                filename = os.path.basename(expected_filename)
                file_path = os.path.join(uploads_dir, filename)
                
                # Verify file exists
                if not os.path.exists(file_path):
                    # Try to find the file with different extension
                    base_name = os.path.splitext(expected_filename)[0]
                    for ext in ['.mp4', '.webm', '.mkv']:
                        test_path = base_name + ext
                        if os.path.exists(test_path):
                            file_path = test_path
                            filename = os.path.basename(file_path)
                            break
                    else:
                        raise FileNotFoundError(f"Downloaded file not found: {expected_filename}")
                
                print(f"✅ Downloaded to: {filename}")
                
                # Extract actual duration using OpenCV
                try:
                    cap = cv2.VideoCapture(file_path)
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    actual_duration = frame_count / fps if fps > 0 else duration
                    cap.release()
                    print(f"🎬 Verified duration: {actual_duration:.1f}s")
                except Exception as e:
                    print(f"⚠️  Could not verify duration: {e}")
                    actual_duration = duration
                
                # Create video record in database
                video = Video(
                    title=video_title,
                    description=f"YouTube video downloaded from: {url}",
                    source_type='local',
                    file_path=filename,
                    duration=actual_duration,
                    uploader_id=uploader_id,
                    category=category,
                    analysis_status='pending'
                )
                
                db.session.add(video)
                db.session.commit()
                
                print(f"💾 Added to database with ID: {video.id}")
                
                return {
                    'success': True,
                    'video_id': video.id,
                    'title': video_title,
                    'filename': filename,
                    'duration': actual_duration
                }
                
        except Exception as e:
            print(f"❌ Error downloading video: {e}")
            return {
                'success': False,
                'error': str(e)
            }

def main():
    """Interactive YouTube video downloader"""
    print("\n" + "="*60)
    print("YOUTUBE VIDEO DOWNLOADER")
    print("="*60 + "\n")
    
    url = input("Enter YouTube URL: ").strip()
    if not url:
        print("❌ No URL provided")
        return
    
    title = input("Enter custom title (or press Enter to use YouTube title): ").strip()
    title = title if title else None
    
    print("\nSelect category:")
    print("1. Discrete Trial")
    print("2. Pivotal Response (PRT)")
    print("3. Functional Routines")
    print("4. None")
    
    category_choice = input("Enter choice (1-4): ").strip()
    category_map = {
        '1': 'discrete_trial',
        '2': 'pivotal_response', 
        '3': 'functional_routines',
        '4': None
    }
    category = category_map.get(category_choice)
    
    print(f"\n🚀 Starting download...")
    result = download_youtube_video(url, title, category)
    
    if result['success']:
        print(f"\n🎉 SUCCESS!")
        print(f"Video ID: {result['video_id']}")
        print(f"Title: {result['title']}")
        print(f"File: {result['filename']}")
        print(f"Duration: {result['duration']:.1f}s")
        print(f"\n✨ Video is ready for AI analysis!")
    else:
        print(f"\n❌ FAILED: {result['error']}")

if __name__ == '__main__':
    main()
