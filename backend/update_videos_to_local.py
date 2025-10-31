"""
Script to update existing URL-based videos to local file videos.
Use this when you have local video files that were originally seeded as URLs.
"""

from app import create_app
from models import db, Video
import os
import shutil
from datetime import datetime

def update_videos_to_local():
    """Update videos from URL type to local file type"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("UPDATE VIDEOS TO LOCAL FILES")
        print("="*60)
        
        # Get all URL-based videos
        url_videos = Video.query.filter_by(source_type='url').all()
        
        if not url_videos:
            print("\n✓ No URL-based videos found. All videos are already local!")
            return
        
        print(f"\nFound {len(url_videos)} URL-based videos:\n")
        
        for i, video in enumerate(url_videos, 1):
            print(f"{i}. ID: {video.id} - {video.title}")
            print(f"   URL: {video.url}")
            print(f"   Category: {video.category}")
            print()
        
        print("\n" + "-"*60)
        print("INSTRUCTIONS:")
        print("-"*60)
        print("1. Place your video files in: backend/uploads/")
        print("2. Name them clearly (e.g., 'discrete_trial_1.mp4')")
        print("3. Enter the video ID and filename below")
        print()
        print("Type 'done' when finished, or 'quit' to exit")
        print("-"*60 + "\n")
        
        updates = []
        
        while True:
            video_id_input = input("Enter Video ID to update (or 'done'/'quit'): ").strip()
            
            if video_id_input.lower() == 'quit':
                print("\n❌ Cancelled. No changes made.")
                return
            
            if video_id_input.lower() == 'done':
                break
            
            try:
                video_id = int(video_id_input)
                video = Video.query.get(video_id)
                
                if not video:
                    print(f"❌ Video ID {video_id} not found. Try again.")
                    continue
                
                if video.source_type == 'local':
                    print(f"⚠️  Video ID {video_id} is already a local file.")
                    continue
                
                filename = input(f"Enter filename in uploads/ folder (e.g., 'video.mp4'): ").strip()
                
                # Check if file exists
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                if not os.path.exists(file_path):
                    print(f"❌ File not found: {file_path}")
                    print(f"   Please place the file in: {app.config['UPLOAD_FOLDER']}")
                    retry = input("   Try again? (y/n): ").strip().lower()
                    if retry != 'y':
                        continue
                    else:
                        continue
                
                # Store update info
                updates.append({
                    'video': video,
                    'filename': filename,
                    'old_url': video.url
                })
                
                print(f"✓ Queued update for: {video.title}")
                print()
                
            except ValueError:
                print("❌ Invalid video ID. Please enter a number.")
                continue
        
        # Apply updates
        if not updates:
            print("\n✓ No updates to apply.")
            return
        
        print("\n" + "="*60)
        print("CONFIRM UPDATES")
        print("="*60)
        
        for update in updates:
            video = update['video']
            print(f"\nVideo: {video.title} (ID: {video.id})")
            print(f"  FROM: URL - {update['old_url']}")
            print(f"  TO:   Local File - {update['filename']}")
        
        confirm = input("\n⚠️  Apply these updates? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("\n❌ Updates cancelled. No changes made.")
            return
        
        # Apply all updates
        for update in updates:
            video = update['video']
            video.source_type = 'local'
            video.file_path = update['filename']
            video.url = None
            video.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ UPDATES COMPLETE!")
        print("="*60)
        print(f"\nUpdated {len(updates)} video(s) to local files.")
        print("\nThese videos can now be analyzed with AI!")
        print("\nNext steps:")
        print("1. Go to the video detail page")
        print("2. Click 'AI Analyze' button")
        print("3. Wait 1-2 minutes for analysis")
        print("="*60 + "\n")


if __name__ == '__main__':
    update_videos_to_local()

