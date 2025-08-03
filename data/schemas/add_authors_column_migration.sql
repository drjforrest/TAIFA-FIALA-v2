-- Migration: Add authors column to publications table
-- Date: 2025-01-03
-- Description: Adds authors column as text array to store publication authors

-- Add the authors column as a text array
ALTER TABLE publications ADD COLUMN authors text[];

-- Create an index for better performance when searching authors
CREATE INDEX IF NOT EXISTS idx_publications_authors ON publications USING gin(authors);

-- Verify the column was added successfully
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'publications' AND column_name = 'authors';

-- Success message
SELECT 'Authors column successfully added to publications table!' as result;
