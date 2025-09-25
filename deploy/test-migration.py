#!/usr/bin/env python3
"""
Test script to verify the context field migration
"""

import os
import sys
import pymysql
from sqlalchemy import create_engine, text

# Configuration
DB_HOST = "34.55.198.147"
DB_PORT = 3306
DB_NAME = "i18n_l10n_db"
DB_USER = "appuser"
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_secure_password_here")

def test_migration():
    """Test the context field migration"""
    try:
        # Direct connection to Cloud SQL
        connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)
        
        with engine.connect() as conn:
            print("✅ Connected to database successfully")
            
            # Check translation_tags table structure
            print("\n--- translation_tags table structure ---")
            result = conn.execute(text("DESCRIBE translation_tags"))
            for row in result:
                print(f"  {row[0]} - {row[1]} - {row[2]}")
            
            # Check translations table structure
            print("\n--- translations table structure ---")
            result = conn.execute(text("DESCRIBE translations"))
            for row in result:
                print(f"  {row[0]} - {row[1]} - {row[2]}")
            
            # Check if context column exists in translation_tags
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'i18n_l10n_db' 
                AND TABLE_NAME = 'translation_tags' 
                AND COLUMN_NAME = 'context'
            """))
            
            if result.fetchone():
                print("\n✅ Context column exists in translation_tags")
            else:
                print("\n❌ Context column missing from translation_tags")
            
            # Check if context column exists in translations
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'i18n_l10n_db' 
                AND TABLE_NAME = 'translations' 
                AND COLUMN_NAME = 'context'
            """))
            
            if result.fetchone():
                print("❌ Context column still exists in translations (should be removed)")
            else:
                print("✅ Context column removed from translations")
            
            # Show sample data
            print("\n--- Sample translation_tags data ---")
            result = conn.execute(text("SELECT id, application, tag, context FROM translation_tags LIMIT 5"))
            for row in result:
                print(f"  ID: {row[0]}, App: {row[1]}, Tag: {row[2]}, Context: {row[3]}")
            
            print("\n✅ Migration test completed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Testing context field migration...")
    test_migration()
