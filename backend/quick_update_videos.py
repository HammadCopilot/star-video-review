"""
Quick script to update specific videos to local files.
Edit the VIDEO_FILES dictionary below with your video IDs and filenames.
"""

from app import create_app
from models import db, Video
import os
from datetime import datetime

# ============================================================
# EDIT THIS: Map video IDs to local filenames
# ============================================================
VIDEO_FILES = {
    # Example:
    # 1: 'video1.mp4',
    # 2: 'video2.mp4',
    # 3: 'discrete_trial_session.mp4',
}

# If you want to update ALL videos with files matching their titles:
AUTO_MATCH = True  # Set to True to auto-match by similar filenames
# ============================================================


def update_videos():
    """Update videos to use local files"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("QUICK UPDATE VIDEOS TO LOCAL FILES")
        print("="*60 + "\n")
        
        uploads_dir = app.config['UPLOAD_FOLDER']
        
        # Get all files in uploads directory
        if os.path.exists(uploads_dir):
            available_files = [f for f in os.listdir(uploads_dir) 
                             if os.path.isfile(os.path.join(uploads_dir, f))]
        else:
            available_files = []
        
        print(f"Files in uploads/ directory: {len(available_files)}")
        if available_files:
            for f in available_files:
                print(f"  • {f}")
        else:
            print("  (No files found)")
        print()
        
        # Get all URL-based videos
        url_videos = Video.query.filter_by(source_type='url').all()
        print(f"URL-based videos in database: {len(url_videos)}")
        for v in url_videos:
            print(f"  {v.id}. {v.title}")
        print()
        
        if not available_files:
            print("❌ No files found in uploads/ directory.")
            print(f"   Please add video files to: {uploads_dir}")
            return
        
        if not url_videos:
            print("✓ No URL-based videos to update!")
            return
        
        updates_made = 0
        
        # Use VIDEO_FILES mapping if provided
        if VIDEO_FILES:
            print("Using VIDEO_FILES mapping...\n")
            for video_id, filename in VIDEO_FILES.items():
                video = Video.query.get(video_id)
                
                if not video:
                    print(f"⚠️  Video ID {video_id} not found")
                    continue
                
                if video.source_type == 'local':
                    print(f"⚠️  Video {video_id} already local")
                    continue
                
                file_path = os.path.join(uploads_dir, filename)
                if not os.path.exists(file_path):
                    print(f"❌ File not found: {filename}")
                    continue
                
                # Update video
                video.source_type = 'local'
                video.file_path = filename
                video.url = None
                video.updated_at = datetime.utcnow()
                
                print(f"✓ Updated: {video.title} → {filename}")
                updates_made += 1
        
        # Auto-match if enabled
        elif AUTO_MATCH and available_files:
            print("Auto-matching files to videos...\n")
            
            for video_file in available_files:
                # Find best matching video
                best_match = None
                filename_lower = video_file.lower().replace('_', ' ').replace('-', ' ')
                
                for video in url_videos:
                    if video.source_type == 'local':
                        continue
                    
                    title_lower = video.title.lower()
                    
                    # Simple matching: check if words from title are in filename
                    if any(word in filename_lower for word in title_lower.split() if len(word) > 3):
                        best_match = video
                        break
                
                if best_match:
                    best_match.source_type = 'local'
                    best_match.file_path = video_file
                    best_match.url = None
                    best_match.updated_at = datetime.utcnow()
                    
                    print(f"✓ Matched: {best_match.title} → {video_file}")
                    updates_made += 1
        
        if updates_made > 0:
            db.session.commit()
            print(f"\n✅ Successfully updated {updates_made} video(s)!")
            print("\nThese videos can now be analyzed with AI.")
        else:
            print("\n⚠️  No updates made.")
            print("\nTo manually specify mappings, edit VIDEO_FILES in this script:")
            print("  VIDEO_FILES = {")
            print("      1: 'your_video1.mp4',")
            print("      2: 'your_video2.mp4',")
            print("  }")
        
        print("="*60 + "\n")


if __name__ == '__main__':
    update_videos()

