#!/usr/bin/env python3
"""
Neon PostgreSQL Setup and Migration Script
==========================================

This script helps you:
1. Test your Neon database connection
2. Create all necessary tables
3. Migrate data from SQLite (if needed)
4. Seed initial data

Usage:
    python setup_neon.py --test-connection
    python setup_neon.py --create-tables
    python setup_neon.py --migrate-from-sqlite
    python setup_neon.py --seed-data
    python setup_neon.py --full-setup
"""

import os
import sys
import argparse
from datetime import datetime
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Video, Annotation, BestPractice, Review, Transcript, AuditLog
from seed_data import seed_database


def test_connection(database_url):
    """Test connection to Neon database"""
    print("🔍 Testing Neon database connection...")
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"📊 PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False


def create_tables(app):
    """Create all database tables"""
    print("🏗️  Creating database tables...")
    
    try:
        with app.app_context():
            db.create_all()
            print("✅ All tables created successfully!")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Created tables: {', '.join(tables)}")
            return True
    except Exception as e:
        print(f"❌ Failed to create tables: {str(e)}")
        return False


def migrate_sqlite_data(app, sqlite_path):
    """Migrate data from SQLite to PostgreSQL"""
    print(f"🔄 Migrating data from SQLite: {sqlite_path}")
    
    if not os.path.exists(sqlite_path):
        print(f"⚠️  SQLite database not found: {sqlite_path}")
        return True  # Not an error if no data to migrate
    
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        
        with app.app_context():
            # Migrate Users
            users_cursor = sqlite_conn.execute("SELECT * FROM users")
            users_data = users_cursor.fetchall()
            
            if users_data:
                print(f"👥 Migrating {len(users_data)} users...")
                for row in users_data:
                    user = User(
                        email=row['email'],
                        password_hash=row['password_hash'],
                        role=row['role'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        is_active=bool(row['is_active']),
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.utcnow()
                    )
                    db.session.add(user)
            
            # Migrate Videos
            videos_cursor = sqlite_conn.execute("SELECT * FROM videos")
            videos_data = videos_cursor.fetchall()
            
            if videos_data:
                print(f"🎥 Migrating {len(videos_data)} videos...")
                for row in videos_data:
                    video = Video(
                        title=row['title'],
                        description=row['description'],
                        source_type=row['source_type'],
                        file_path=row['file_path'],
                        url=row['url'],
                        duration=row['duration'],
                        thumbnail_path=row['thumbnail_path'],
                        uploader_id=row['uploader_id'],
                        category=row['category'],
                        is_analyzed=bool(row['is_analyzed']),
                        analysis_status=row['analysis_status'],
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.utcnow()
                    )
                    db.session.add(video)
            
            # Commit the migration
            db.session.commit()
            print("✅ Data migration completed successfully!")
            
        sqlite_conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False


def seed_initial_data(app):
    """Seed initial data (users, best practices, sample videos)"""
    print("🌱 Seeding initial data...")
    
    try:
        # The seed_database function creates its own app context, so we don't need to wrap it
        seed_database()
        print("✅ Initial data seeded successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to seed data: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Neon PostgreSQL Setup Script')
    parser.add_argument('--test-connection', action='store_true', help='Test database connection')
    parser.add_argument('--create-tables', action='store_true', help='Create database tables')
    parser.add_argument('--migrate-from-sqlite', action='store_true', help='Migrate data from SQLite')
    parser.add_argument('--seed-data', action='store_true', help='Seed initial data')
    parser.add_argument('--full-setup', action='store_true', help='Run complete setup')
    parser.add_argument('--sqlite-path', default='star_video_review.db', help='Path to SQLite database')
    
    args = parser.parse_args()
    
    # Check for DATABASE_URL environment variable
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        print("💡 Please set your Neon connection string:")
        print("   export DATABASE_URL='postgresql://username:password@host/database?sslmode=require'")
        return 1
    
    if not database_url.startswith('postgresql://'):
        print("⚠️  DATABASE_URL doesn't appear to be a PostgreSQL connection string")
        print(f"   Current value: {database_url}")
    
    # Create Flask app
    app = create_app('development')
    
    success = True
    
    if args.test_connection or args.full_setup:
        success &= test_connection(database_url)
    
    if args.create_tables or args.full_setup:
        if success:
            success &= create_tables(app)
    
    if args.migrate_from_sqlite or args.full_setup:
        if success:
            success &= migrate_sqlite_data(app, args.sqlite_path)
    
    if args.seed_data or args.full_setup:
        if success:
            success &= seed_initial_data(app)
    
    if not any([args.test_connection, args.create_tables, args.migrate_from_sqlite, args.seed_data, args.full_setup]):
        parser.print_help()
        return 1
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("🚀 Your application is ready to use Neon PostgreSQL!")
    else:
        print("\n💥 Setup encountered errors. Please check the output above.")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
