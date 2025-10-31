"""
Download URL-based videos to local files for AI analysis
"""

from app import create_app
from models import db, Video
import os
import requests
from datetime import datetime
from urllib.parse import urlparse
import time

def download_video(url, output_path):
    """Download video from URL"""
    print(f"  Downloading from: {url}")
    print(f"  Saving to: {output_path}")
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        percent = (downloaded / total_size) * 100
                        print(f"  Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='\r')
        
        print(f"\n  ✓ Download complete: {downloaded} bytes")
        return True
        
    except Exception as e:
        print(f"\n  ✗ Download failed: {e}")
        return False


def download_all_url_videos():
    """Download all URL-based videos"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("DOWNLOAD URL VIDEOS FOR AI ANALYSIS")
        print("="*60 + "\n")
        
        uploads_dir = app.config['UPLOAD_FOLDER']
        
        # Create uploads directory if it doesn't exist
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            print(f"✓ Created uploads directory: {uploads_dir}\n")
        
        # Get all URL-based videos
        url_videos = Video.query.filter_by(source_type='url').all()
        
        if not url_videos:
            print("✓ No URL-based videos found. All videos are already local!")
            return
        
        print(f"Found {len(url_videos)} URL-based videos:\n")
        
        for i, video in enumerate(url_videos, 1):
            print(f"{i}. ID: {video.id} - {video.title}")
            print(f"   Category: {video.category}")
            print(f"   URL: {video.url[:60]}...")
            print()
        
        print("-"*60)
        choice = input("\nDownload ALL videos? (yes/no/select): ").strip().lower()
        
        if choice == 'no':
            print("\n❌ Cancelled.")
            return
        
        videos_to_download = []
        
        if choice == 'select':
            print("\nEnter video IDs to download (comma-separated, e.g., 1,2,3):")
            ids_input = input("IDs: ").strip()
            selected_ids = [int(x.strip()) for x in ids_input.split(',') if x.strip()]
            videos_to_download = [v for v in url_videos if v.id in selected_ids]
        else:
            videos_to_download = url_videos
        
        if not videos_to_download:
            print("\n❌ No videos selected.")
            return
        
        print(f"\n{'='*60}")
        print(f"DOWNLOADING {len(videos_to_download)} VIDEO(S)")
        print("="*60 + "\n")
        
        success_count = 0
        failed_count = 0
        
        for i, video in enumerate(videos_to_download, 1):
            print(f"\n[{i}/{len(videos_to_download)}] {video.title}")
            print("-"*60)
            
            # Generate filename
            # Extract extension from URL
            parsed_url = urlparse(video.url)
            path_parts = parsed_url.path.split('.')
            extension = path_parts[-1] if len(path_parts) > 1 else 'mp4'
            
            # Clean title for filename
            safe_title = "".join(c for c in video.title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{safe_title}.{extension}"
            output_path = os.path.join(uploads_dir, filename)
            
            # Download video
            if download_video(video.url, output_path):
                # Update database
                video.source_type = 'local'
                video.file_path = filename
                video.url = None  # Clear URL
                video.updated_at = datetime.utcnow()
                
                success_count += 1
                print(f"  ✓ Updated database: {video.title}")
            else:
                failed_count += 1
                print(f"  ✗ Failed to download: {video.title}")
                # Delete partial file if exists
                if os.path.exists(output_path):
                    os.remove(output_path)
            
            # Small delay between downloads
            if i < len(videos_to_download):
                time.sleep(1)
        
        # Commit all changes
        if success_count > 0:
            db.session.commit()
        
        print("\n" + "="*60)
        print("DOWNLOAD COMPLETE")
        print("="*60)
        print(f"\n✅ Successfully downloaded: {success_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"\nTotal: {len(videos_to_download)}")
        
        if success_count > 0:
            print("\n🎉 Videos are now ready for AI analysis!")
            print("\nNext steps:")
            print("1. Refresh your dashboard")
            print("2. Click any downloaded video")
            print("3. Click 'AI Analyze' button")
            print("4. Wait 1-2 minutes")
            print("5. See AI-generated annotations!")
        
        print("="*60 + "\n")


if __name__ == '__main__':
    download_all_url_videos()

