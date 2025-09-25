-- Migration to move context from translations to translation_tags
-- This script should be run on the Cloud SQL instance

-- Add context column to translation_tags table
ALTER TABLE translation_tags ADD COLUMN context VARCHAR(500) NULL;

-- Migrate existing context data from translations to translation_tags
-- Copy context from the first translation of each tag that has context
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
);

-- Remove context column from translations table
ALTER TABLE translations DROP COLUMN context;

-- Show the updated structure
DESCRIBE translation_tags;
DESCRIBE translations;
