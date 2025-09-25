#!/usr/bin/env python3
"""
Test script to directly test database connection and query translation tags
"""
import os
import sys
from i18n_l10n.database import DatabaseManager

def test_database_direct():
    """Test database connection and query translation tags directly"""
    print("=== Testing Database Connection Directly ===")
    
    # Set environment variables for Cloud SQL
    os.environ['DB_CONNECTION_NAME'] = 'i18n-l10n:europe-north1:i18n-l10n-mysql'
    os.environ['DB_NAME'] = 'i18n_l10n_db'
    os.environ['DB_USER'] = 'appuser'
    os.environ['DB_PASSWORD'] = 'i18n-l10n-secure-password-2024'
    
    try:
        db_manager = DatabaseManager()
        print("✅ Database manager created successfully")
        
        # Test connection
        from sqlalchemy import text
        with db_manager.get_session() as session:
            result = session.execute(text("SELECT 1 as test")).fetchone()
            print(f"✅ Database connection successful: {result}")
        
        # Test getting all translation tags
        print("\n--- Testing get_all_translation_tags ---")
        tags = db_manager.get_all_translation_tags()
        print(f"Found {len(tags)} translation tags")
        
        for i, tag in enumerate(tags):
            print(f"Tag {i+1}: {tag}")
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_direct()
