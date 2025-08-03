-- Check the current authors column data type and structure
-- This will help us understand what's causing the schema cache error

-- Check if authors column exists and its data type
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default,
    udt_name  -- This shows the underlying PostgreSQL type
FROM information_schema.columns 
WHERE table_name = 'publications' AND column_name = 'authors';

-- Also check if there's any data in the authors column
SELECT 
    COUNT(*) as total_publications,
    COUNT(authors) as publications_with_authors,
    COUNT(*) - COUNT(authors) as publications_without_authors
FROM publications;

-- Show a few sample authors values to understand the current format
SELECT id, title, authors 
FROM publications 
WHERE authors IS NOT NULL 
LIMIT 5;
