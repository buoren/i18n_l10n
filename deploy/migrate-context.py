#!/usr/bin/env python3
"""
Migration script to move context from Translation to TranslationTag
This script connects to Cloud SQL and runs the migration.
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

def get_connection():
    """Get database connection"""
    try:
        # Direct connection to Cloud SQL
        connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        print(f"Connection failed: {e}")
        raise

def run_migration():
    """Run the context field migration"""
    try:
        engine = get_connection()
        
        with engine.connect() as conn:
            print("Connected to database successfully")
            
            # Check if context column exists in translation_tags
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'i18n_l10n_db' 
                AND TABLE_NAME = 'translation_tags' 
                AND COLUMN_NAME = 'context'
            """))
            
            if result.fetchone():
                print("✅ Context column already exists in translation_tags")
            else:
                print("Adding context column to translation_tags...")
                conn.execute(text("ALTER TABLE translation_tags ADD COLUMN context VARCHAR(500) NULL"))
                conn.commit()
                print("✅ Added context column to translation_tags")
            
            # Check if context column exists in translations
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'i18n_l10n_db' 
                AND TABLE_NAME = 'translations' 
                AND COLUMN_NAME = 'context'
            """))
            
            if result.fetchone():
                print("Migrating context data from translations to translation_tags...")
                
                # Migrate existing context data
                conn.execute(text("""
                    UPDATE translation_tags tt
                    SET context = (
                        SELECT t.context 
                        FROM translations t 
                        WHERE t.translation_tag_id = tt.id 
                        AND t.context IS NOT NULL 
                        LIMIT 1
                    )
                    WHERE EXISTS (
                        SELECT 1 FROM translations t 
                        WHERE t.translation_tag_id = tt.id 
                        AND t.context IS NOT NULL
                    )
                """))
                conn.commit()
                print("✅ Migrated context data")
                
                # Remove context column from translations
                print("Removing context column from translations...")
                conn.execute(text("ALTER TABLE translations DROP COLUMN context"))
                conn.commit()
                print("✅ Removed context column from translations")
            else:
                print("✅ Context column already removed from translations")
            
            # Show updated structure
            print("\n--- Updated table structures ---")
            print("\ntranslation_tags:")
            result = conn.execute(text("DESCRIBE translation_tags"))
            for row in result:
                print(f"  {row[0]} - {row[1]} - {row[2]}")
            
            print("\ntranslations:")
            result = conn.execute(text("DESCRIBE translations"))
            for row in result:
                print(f"  {row[0]} - {row[1]} - {row[2]}")
            
            print("\n✅ Migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting context field migration...")
    run_migration()
