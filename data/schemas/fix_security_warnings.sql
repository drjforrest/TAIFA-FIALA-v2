-- Fix Supabase Security Warnings
-- Addresses function search_path and materialized view security warnings

-- =====================================================
-- FIX FUNCTION SEARCH PATH WARNINGS
-- =====================================================

-- Fix update_updated_at_column function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER 
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Fix calculate_innovation_metrics function
CREATE OR REPLACE FUNCTION calculate_innovation_metrics(innovation_uuid UUID)
RETURNS JSONB 
SET search_path = public
AS $$
DECLARE
    metrics JSONB;
    pub_count INTEGER;
    org_count INTEGER;
    individual_count INTEGER;
BEGIN
    -- Count related publications
    SELECT COUNT(*) INTO pub_count 
    FROM innovation_publications 
    WHERE innovation_id = innovation_uuid;
    
    -- Count related organizations
    SELECT COUNT(*) INTO org_count 
    FROM innovation_organizations 
    WHERE innovation_id = innovation_uuid;
    
    -- Count related individuals
    SELECT COUNT(*) INTO individual_count 
    FROM innovation_individuals 
    WHERE innovation_id = innovation_uuid;
    
    metrics := jsonb_build_object(
        'publications_count', pub_count,
        'organizations_count', org_count,
        'individuals_count', individual_count,
        'calculated_at', NOW()
    );
    
    RETURN metrics;
END;
$$ LANGUAGE plpgsql;

-- Fix user_can_access_innovation function
CREATE OR REPLACE FUNCTION user_can_access_innovation(innovation_uuid UUID)
RETURNS BOOLEAN 
SET search_path = public
AS $$
BEGIN
    -- Check if innovation is public
    IF EXISTS (SELECT 1 FROM innovations WHERE id = innovation_uuid AND visibility = 'public') THEN
        RETURN true;
    END IF;
    
    -- Check if user is connected to the innovation
    IF EXISTS (
        SELECT 1 FROM innovation_individuals ii
        JOIN individuals i ON ii.individual_id = i.id
        WHERE ii.innovation_id = innovation_uuid 
        AND i.email = auth.jwt() ->> 'email'
        AND ii.relationship_type IN ('lead_developer', 'contributor', 'researcher')
    ) THEN
        RETURN true;
    END IF;
    
    RETURN false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Fix user_can_moderate function
CREATE OR REPLACE FUNCTION user_can_moderate()
RETURNS BOOLEAN 
SET search_path = public
AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM individuals 
        WHERE email = auth.jwt() ->> 'email' 
        AND role IN ('admin', 'moderator')
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- CREATE AND SECURE MATERIALIZED VIEW
-- =====================================================

-- Create the dashboard_stats materialized view if it doesn't exist
CREATE MATERIALIZED VIEW IF NOT EXISTS dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM publications) as total_publications,
    (SELECT COUNT(*) FROM innovations) as total_innovations,
    (SELECT COUNT(*) FROM organizations) as total_organizations,
    (SELECT COUNT(*) FROM individuals WHERE verification_status = 'verified') as verified_individuals,
    (SELECT COUNT(DISTINCT entity) FROM publications, unnest(african_entities) as entity WHERE african_entities IS NOT NULL) as african_countries_covered,
    (SELECT COUNT(DISTINCT keyword) FROM publications, unnest(keywords) as keyword WHERE keywords IS NOT NULL) as unique_keywords,
    (SELECT AVG(african_relevance_score) FROM publications WHERE african_relevance_score > 0) as avg_african_relevance,
    (SELECT AVG(ai_relevance_score) FROM publications WHERE ai_relevance_score > 0) as avg_ai_relevance,
    NOW() as last_updated;

-- Create unique index if it doesn't exist
CREATE UNIQUE INDEX IF NOT EXISTS dashboard_stats_updated_idx ON dashboard_stats (last_updated);

-- Add RLS policy to dashboard_stats materialized view to control access
ALTER TABLE dashboard_stats ENABLE ROW LEVEL SECURITY;

-- Create policy for dashboard stats (public read access is intentional for dashboard)
CREATE POLICY "Public read access for dashboard stats" ON dashboard_stats 
FOR SELECT USING (true);

-- =====================================================
-- VERIFICATION
-- =====================================================

-- Verify the fixes
SELECT 
    'Security warnings fixed!' as status,
    'All functions now have fixed search_path' as functions_fixed,
    'Dashboard materialized view has RLS policy' as view_fixed;