#!/usr/bin/env python3
"""
Simple Neon Connection Test
===========================

This script tests your Neon database connection without loading heavy dependencies
like moviepy, whisper, etc. that are causing NumPy compatibility issues.

Usage:
    python test_neon_connection.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Try to load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except (ImportError, PermissionError):
    # If dotenv fails or .env file is not accessible, continue without it
    print("ℹ️  Note: .env file not loaded (this is okay if you set DATABASE_URL manually)")

def test_neon_connection():
    """Test connection to Neon database"""
    print("🔍 Testing Neon database connection...")
    
    # Get DATABASE_URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        print("💡 Please set your Neon connection string:")
        print("   export DATABASE_URL='postgresql://username:password@host/database?sslmode=require'")
        print("\n📝 Or create a .env file with:")
        print("   DATABASE_URL=postgresql://username:password@host/database?sslmode=require")
        return False
    
    if not database_url.startswith('postgresql://'):
        print("⚠️  DATABASE_URL doesn't appear to be a PostgreSQL connection string")
        print(f"   Current value: {database_url}")
        return False
    
    # Handle SSL requirements for Neon
    if 'sslmode=' not in database_url:
        database_url += '?sslmode=require'
        print("🔒 Added SSL requirement to connection string")
    
    try:
        print(f"🔗 Connecting to: {database_url.split('@')[0]}@***")
        
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"📊 PostgreSQL version: {version}")
            
            # Test if we can create a simple table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS connection_test (
                    id SERIAL PRIMARY KEY,
                    test_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Insert a test record
            conn.execute(text("""
                INSERT INTO connection_test (test_message) 
                VALUES ('Neon connection test successful!')
            """))
            
            # Read it back
            result = conn.execute(text("SELECT test_message, created_at FROM connection_test ORDER BY created_at DESC LIMIT 1"))
            row = result.fetchone()
            
            print(f"✅ Database write/read test successful!")
            print(f"📝 Test message: {row[0]}")
            print(f"⏰ Created at: {row[1]}")
            
            # Clean up test table
            conn.execute(text("DROP TABLE connection_test"))
            conn.commit()
            
            print("🧹 Cleaned up test table")
            print("\n🎉 Your Neon database is ready to use!")
            
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your DATABASE_URL is correct")
        print("2. Verify your Neon database is running")
        print("3. Ensure your IP is allowed (Neon allows all by default)")
        print("4. Check if the database name exists")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def show_next_steps():
    """Show next steps after successful connection"""
    print("\n🚀 Next Steps:")
    print("1. Fix NumPy compatibility issues:")
    print("   pip install --upgrade --force-reinstall numpy==1.26.4")
    print("   pip install --upgrade --force-reinstall -r requirements.txt")
    print("\n2. Then run the full setup:")
    print("   python setup_neon.py --full-setup")
    print("\n3. Or run individual steps:")
    print("   python setup_neon.py --create-tables")
    print("   python setup_neon.py --seed-data")


if __name__ == '__main__':
    print("🌟 STAR Video Review - Neon Connection Test")
    print("=" * 50)
    
    success = test_neon_connection()
    
    if success:
        show_next_steps()
        sys.exit(0)
    else:
        print("\n💥 Connection test failed. Please check your configuration.")
        sys.exit(1)
