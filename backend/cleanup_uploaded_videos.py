#!/usr/bin/env python3
"""
Cleanup Script: Delete Uploaded Video Files to Free Disk Space

This script removes all uploaded video files from the uploads folder while keeping the database records.
Videos with source_type='local' will have their file_path cleared but remain as URL-based entries
if they have an original URL stored in video_metadata.

Run this script AFTER deploying the new version that uses temporary downloads.
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Video


def cleanup_uploaded_videos(dry_run=True):
    """
    Delete uploaded video files and update database records
    
    Args:
        dry_run: If True, only show what would be deleted without actually deleting
    """
    app = create_app()
    
    with app.app_context():
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        
        # Find all locally uploaded videos
        local_videos = Video.query.filter_by(source_type='local').all()
        
        print(f"{'=' * 70}")
        print(f"VIDEO CLEANUP SCRIPT - {'DRY RUN' if dry_run else 'LIVE MODE'}")
        print(f"{'=' * 70}\n")
        
        total_size = 0
        deleted_count = 0
        kept_count = 0
        
        for video in local_videos:
            if not video.file_path:
                continue
            
            file_path = os.path.join(upload_folder, video.file_path)
            
            # Check if file exists
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                total_size += file_size
                size_mb = file_size / (1024 * 1024)
                
                print(f"Video ID: {video.id}")
                print(f"  Title: {video.title}")
                print(f"  File: {video.file_path}")
                print(f"  Size: {size_mb:.2f} MB")
                
                # Check if we have original URL in metadata
                has_url = False
                if video.video_metadata:
                    try:
                        metadata = json.loads(video.video_metadata)
                        if 'original_url' in metadata and metadata['original_url']:
                            has_url = True
                            print(f"  Original URL: {metadata['original_url']}")
                    except:
                        pass
                
                if video.url:
                    has_url = True
                    print(f"  URL: {video.url}")
                
                if not dry_run:
                    # Delete the file
                    try:
                        os.remove(file_path)
                        print(f"  ✅ File deleted")
                        
                        # Update database record
                        if has_url:
                            # Keep as URL-based video
                            if not video.url and video.video_metadata:
                                metadata = json.loads(video.video_metadata)
                                video.url = metadata.get('original_url')
                            video.source_type = 'url'
                            video.file_path = None
                            print(f"  ✅ Converted to URL-based video")
                        else:
                            # No URL available, mark as unavailable
                            video.file_path = None
                            print(f"  ⚠️  No URL available - video marked as unavailable")
                        
                        db.session.commit()
                        deleted_count += 1
                        
                    except Exception as e:
                        print(f"  ❌ Error: {e}")
                        kept_count += 1
                else:
                    print(f"  🔍 Would be deleted")
                    deleted_count += 1
                
                print()
            else:
                print(f"Video ID: {video.id} - File not found: {video.file_path}")
                if not dry_run:
                    # Clean up database entry
                    video.file_path = None
                    db.session.commit()
                print()
        
        total_mb = total_size / (1024 * 1024)
        total_gb = total_size / (1024 * 1024 * 1024)
        
        print(f"{'=' * 70}")
        print(f"SUMMARY")
        print(f"{'=' * 70}")
        print(f"Total videos found: {len(local_videos)}")
        print(f"Videos to delete: {deleted_count}")
        print(f"Videos kept: {kept_count}")
        print(f"Total size: {total_mb:.2f} MB ({total_gb:.2f} GB)")
        print(f"{'=' * 70}\n")
        
        if dry_run:
            print("⚠️  This was a DRY RUN - no files were actually deleted")
            print("   Run with --execute flag to actually delete files\n")
        else:
            print("✅ Cleanup complete!")
            print(f"   Freed up {total_mb:.2f} MB ({total_gb:.2f} GB) of disk space\n")


def list_upload_folder():
    """List all files in the uploads folder"""
    app = create_app()
    
    with app.app_context():
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        
        if not os.path.exists(upload_folder):
            print(f"Upload folder not found: {upload_folder}")
            return
        
        files = []
        total_size = 0
        
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                files.append((filename, size))
                total_size += size
        
        print(f"\n{'=' * 70}")
        print(f"UPLOAD FOLDER CONTENTS: {upload_folder}")
        print(f"{'=' * 70}\n")
        
        for filename, size in sorted(files, key=lambda x: x[1], reverse=True):
            size_mb = size / (1024 * 1024)
            print(f"{filename:<50} {size_mb:>10.2f} MB")
        
        total_mb = total_size / (1024 * 1024)
        total_gb = total_size / (1024 * 1024 * 1024)
        
        print(f"\n{'=' * 70}")
        print(f"Total files: {len(files)}")
        print(f"Total size: {total_mb:.2f} MB ({total_gb:.2f} GB)")
        print(f"{'=' * 70}\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Clean up uploaded video files to free disk space'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually delete files (default is dry-run)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all files in upload folder'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_upload_folder()
    else:
        cleanup_uploaded_videos(dry_run=not args.execute)

