-- TAIFA-FIALA Database Schema UPDATE for Supabase
-- Handles existing tables and adds RLS policies
-- Safe to run multiple times

-- =====================================================
-- DROP EXISTING POLICIES (if any)
-- =====================================================

-- Drop all existing policies to avoid conflicts
DO $$ 
DECLARE
    r RECORD;
BEGIN
    -- Drop all policies on all tables
    FOR r IN (SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON ' || r.schemaname || '.' || r.tablename;
    END LOOP;
END $$;

-- =====================================================
-- CREATE TABLES (IF NOT EXISTS)
-- =====================================================

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  organization_type TEXT NOT NULL,
  country TEXT NOT NULL,
  website TEXT,
  description TEXT,
  founded_date DATE,
  contact_email TEXT,
  logo_url TEXT,
  verification_status TEXT DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individuals table
CREATE TABLE IF NOT EXISTS individuals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  role TEXT,
  bio TEXT,
  country TEXT,
  organization_id UUID REFERENCES organizations(id),
  linkedin_url TEXT,
  twitter_url TEXT,
  website_url TEXT,
  orcid_id TEXT,
  profile_image_url TEXT,
  expertise_areas TEXT[],
  verification_status TEXT DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Publications table
CREATE TABLE IF NOT EXISTS publications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  abstract TEXT,
  publication_type TEXT NOT NULL,
  publication_date DATE,
  year INTEGER,
  doi TEXT,
  url TEXT,
  pdf_url TEXT,
  journal TEXT,
  venue TEXT,
  citation_count INTEGER DEFAULT 0,
  project_domain TEXT,
  ai_techniques TEXT,
  geographic_scope TEXT,
  funding_source TEXT,
  key_outcomes TEXT,
  african_relevance_score DECIMAL(3,2) DEFAULT 0.0,
  ai_relevance_score DECIMAL(3,2) DEFAULT 0.0,
  african_entities TEXT[],
  keywords TEXT[],
  source TEXT NOT NULL,
  source_id TEXT,
  data_type TEXT DEFAULT 'Academic Paper',
  processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  verification_status TEXT DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Innovations table
CREATE TABLE IF NOT EXISTS innovations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  innovation_type TEXT NOT NULL,
  domain TEXT NOT NULL,
  ai_techniques_used TEXT[],
  target_beneficiaries TEXT,
  problem_addressed TEXT,
  solution_approach TEXT,
  development_stage TEXT DEFAULT 'concept',
  technology_stack TEXT[],
  programming_languages TEXT[],
  datasets_used TEXT[],
  countries_deployed TEXT[],
  target_countries TEXT[],
  users_reached INTEGER DEFAULT 0,
  impact_metrics JSONB,
  verification_status TEXT DEFAULT 'pending',
  visibility TEXT DEFAULT 'public',
  demo_url TEXT,
  github_url TEXT,
  documentation_url TEXT,
  video_url TEXT,
  image_urls TEXT[],
  creation_date DATE,
  last_updated_date DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fundings table
CREATE TABLE IF NOT EXISTS fundings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  innovation_id UUID REFERENCES innovations(id),
  funder_org_id UUID REFERENCES organizations(id),
  funding_type TEXT NOT NULL,
  amount DECIMAL(15,2),
  currency TEXT DEFAULT 'USD',
  funding_date DATE,
  duration_months INTEGER,
  description TEXT,
  funding_program TEXT,
  verification_status TEXT DEFAULT 'pending',
  verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Relationship tables
CREATE TABLE IF NOT EXISTS innovation_organizations (
  innovation_id UUID REFERENCES innovations(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  relationship_type TEXT NOT NULL,
  role_description TEXT,
  start_date DATE,
  end_date DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (innovation_id, organization_id, relationship_type)
);

CREATE TABLE IF NOT EXISTS innovation_individuals (
  innovation_id UUID REFERENCES innovations(id) ON DELETE CASCADE,
  individual_id UUID REFERENCES individuals(id) ON DELETE CASCADE,
  relationship_type TEXT NOT NULL,
  role_description TEXT,
  contribution_details TEXT,
  start_date DATE,
  end_date DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (innovation_id, individual_id, relationship_type)
);

CREATE TABLE IF NOT EXISTS innovation_publications (
  innovation_id UUID REFERENCES innovations(id) ON DELETE CASCADE,
  publication_id UUID REFERENCES publications(id) ON DELETE CASCADE,
  relationship_type TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (innovation_id, publication_id)
);

CREATE TABLE IF NOT EXISTS publication_authors (
  publication_id UUID REFERENCES publications(id) ON DELETE CASCADE,
  individual_id UUID REFERENCES individuals(id) ON DELETE CASCADE,
  author_order INTEGER,
  affiliation TEXT,
  corresponding_author BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (publication_id, individual_id)
);

CREATE TABLE IF NOT EXISTS publication_organizations (
  publication_id UUID REFERENCES publications(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  relationship_type TEXT DEFAULT 'affiliation',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (publication_id, organization_id)
);

-- Vector storage and content tables
CREATE TABLE IF NOT EXISTS embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_type TEXT NOT NULL,
  source_id UUID NOT NULL,
  vector_id TEXT NOT NULL,
  embedding_model TEXT DEFAULT 'sentence-transformers',
  vector_dimension INTEGER DEFAULT 384,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT,
  summary TEXT,
  url TEXT,
  source_name TEXT,
  source_type TEXT,
  article_type TEXT DEFAULT 'news',
  topics TEXT[],
  countries_mentioned TEXT[],
  organizations_mentioned TEXT[],
  published_date TIMESTAMP WITH TIME ZONE,
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  author TEXT,
  image_url TEXT,
  african_relevance_score DECIMAL(3,2) DEFAULT 0.0,
  ai_relevance_score DECIMAL(3,2) DEFAULT 0.0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content TEXT NOT NULL,
  parent_id UUID REFERENCES comments(id),
  target_type TEXT NOT NULL,
  target_id UUID NOT NULL,
  author_id UUID REFERENCES individuals(id),
  author_name TEXT,
  author_email TEXT,
  status TEXT DEFAULT 'pending',
  moderated_by UUID REFERENCES individuals(id),
  moderated_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ratings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  target_type TEXT NOT NULL,
  target_id UUID NOT NULL,
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  review_text TEXT,
  criteria JSONB,
  rater_id UUID REFERENCES individuals(id),
  rater_expertise TEXT,
  verified_rating BOOLEAN DEFAULT FALSE,
  verification_method TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(target_type, target_id, rater_id)
);

-- System tables
CREATE TABLE IF NOT EXISTS legacy_funding_announcements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  original_data JSONB NOT NULL,
  source_system TEXT,
  archived_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  migrated_to_innovation_id UUID REFERENCES innovations(id),
  migration_notes TEXT
);

CREATE TABLE IF NOT EXISTS ingestion_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_type TEXT NOT NULL,
  status TEXT NOT NULL,
  records_processed INTEGER DEFAULT 0,
  records_inserted INTEGER DEFAULT 0,
  records_updated INTEGER DEFAULT 0,
  error_message TEXT,
  processing_time_seconds INTEGER,
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS user_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT NOT NULL,
  user_id UUID REFERENCES individuals(id),
  ip_address INET,
  user_agent TEXT,
  country TEXT,
  pages_visited TEXT[],
  search_queries TEXT[],
  session_duration_seconds INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ended_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- CREATE INDEXES (IF NOT EXISTS)
-- =====================================================

-- Text search indexes
CREATE INDEX IF NOT EXISTS idx_publications_title_search ON publications USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_publications_abstract_search ON publications USING gin(to_tsvector('english', abstract));
CREATE INDEX IF NOT EXISTS idx_innovations_title_search ON innovations USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_innovations_description_search ON innovations USING gin(to_tsvector('english', description));
CREATE INDEX IF NOT EXISTS idx_organizations_name_search ON organizations USING gin(to_tsvector('english', name));

-- Array indexes
CREATE INDEX IF NOT EXISTS idx_publications_keywords ON publications USING gin(keywords);
CREATE INDEX IF NOT EXISTS idx_publications_african_entities ON publications USING gin(african_entities);
CREATE INDEX IF NOT EXISTS idx_innovations_ai_techniques ON innovations USING gin(ai_techniques_used);
CREATE INDEX IF NOT EXISTS idx_innovations_countries ON innovations USING gin(countries_deployed);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_publications_year ON publications(year);
CREATE INDEX IF NOT EXISTS idx_publications_african_score ON publications(african_relevance_score);
CREATE INDEX IF NOT EXISTS idx_publications_ai_score ON publications(ai_relevance_score);
CREATE INDEX IF NOT EXISTS idx_publications_source ON publications(source);
CREATE INDEX IF NOT EXISTS idx_innovations_domain ON innovations(domain);
CREATE INDEX IF NOT EXISTS idx_innovations_verification_status ON innovations(verification_status);
CREATE INDEX IF NOT EXISTS idx_organizations_country ON organizations(country);
CREATE INDEX IF NOT EXISTS idx_individuals_country ON individuals(country);

-- Compound indexes
CREATE INDEX IF NOT EXISTS idx_publications_african_ai_scores ON publications(african_relevance_score, ai_relevance_score);
CREATE INDEX IF NOT EXISTS idx_publications_year_source ON publications(year, source);
CREATE INDEX IF NOT EXISTS idx_innovations_domain_stage ON innovations(domain, development_stage);

-- =====================================================
-- ENABLE ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE individuals ENABLE ROW LEVEL SECURITY;
ALTER TABLE publications ENABLE ROW LEVEL SECURITY;
ALTER TABLE innovations ENABLE ROW LEVEL SECURITY;
ALTER TABLE fundings ENABLE ROW LEVEL SECURITY;
ALTER TABLE innovation_organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE innovation_individuals ENABLE ROW LEVEL SECURITY;
ALTER TABLE innovation_publications ENABLE ROW LEVEL SECURITY;
ALTER TABLE publication_authors ENABLE ROW LEVEL SECURITY;
ALTER TABLE publication_organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ratings ENABLE ROW LEVEL SECURITY;
ALTER TABLE legacy_funding_announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE ingestion_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- CREATE RLS POLICIES
-- =====================================================

-- PUBLIC READ POLICIES
CREATE POLICY "Public read access for organizations" ON organizations FOR SELECT USING (true);
CREATE POLICY "Public read access for publications" ON publications FOR SELECT USING (true);
CREATE POLICY "Public read access for public innovations" ON innovations FOR SELECT USING (visibility = 'public');
CREATE POLICY "Public read access for articles" ON articles FOR SELECT USING (true);
CREATE POLICY "Public read access for embeddings" ON embeddings FOR SELECT USING (true);
CREATE POLICY "Public read for innovation_organizations" ON innovation_organizations FOR SELECT USING (innovation_id IN (SELECT id FROM innovations WHERE visibility = 'public'));
CREATE POLICY "Public read for innovation_publications" ON innovation_publications FOR SELECT USING (true);
CREATE POLICY "Public read for publication_authors" ON publication_authors FOR SELECT USING (true);
CREATE POLICY "Public read for publication_organizations" ON publication_organizations FOR SELECT USING (true);

-- INDIVIDUAL PRIVACY POLICIES
CREATE POLICY "Public read for verified individuals" ON individuals FOR SELECT USING (verification_status = 'verified');
CREATE POLICY "Users can read their own data" ON individuals FOR SELECT USING (auth.uid()::text = email);
CREATE POLICY "Users can update their own data" ON individuals FOR UPDATE USING (auth.uid()::text = email);
CREATE POLICY "Public read for verified individual connections" ON innovation_individuals FOR SELECT USING (individual_id IN (SELECT id FROM individuals WHERE verification_status = 'verified') AND innovation_id IN (SELECT id FROM innovations WHERE visibility = 'public'));
CREATE POLICY "Users can read their own innovation connections" ON innovation_individuals FOR SELECT USING (individual_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email'));

-- CONTENT CREATION POLICIES
CREATE POLICY "Public read approved comments" ON comments FOR SELECT USING (status = 'approved');
CREATE POLICY "Users can read their own comments" ON comments FOR SELECT USING (author_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email'));
CREATE POLICY "Authenticated users can create comments" ON comments FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update their own comments" ON comments FOR UPDATE USING (author_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email'));

-- RATING POLICIES
CREATE POLICY "Public read for ratings" ON ratings FOR SELECT USING (true);
CREATE POLICY "Authenticated users can create ratings" ON ratings FOR INSERT WITH CHECK (auth.role() = 'authenticated' AND rater_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email'));
CREATE POLICY "Users can update their own ratings" ON ratings FOR UPDATE USING (rater_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email'));

-- INNOVATION MANAGEMENT POLICIES
CREATE POLICY "Authenticated users can create innovations" ON innovations FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update innovations they're connected to" ON innovations FOR UPDATE USING (id IN (SELECT innovation_id FROM innovation_individuals WHERE individual_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email') AND relationship_type IN ('lead_developer', 'contributor')));

-- FUNDING POLICIES
CREATE POLICY "Public read for verified fundings" ON fundings FOR SELECT USING (verified = true);
CREATE POLICY "Authenticated users can create funding records" ON fundings FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- SYSTEM POLICIES
CREATE POLICY "Service role access for ingestion logs" ON ingestion_logs FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Users can read their own sessions" ON user_sessions FOR SELECT USING (user_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email'));
CREATE POLICY "System can manage user sessions" ON user_sessions FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Public read for legacy data" ON legacy_funding_announcements FOR SELECT USING (true);

-- SERVICE ROLE POLICIES (for ETL)
CREATE POLICY "Service role full access to organizations" ON organizations FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access to publications" ON publications FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access to innovations" ON innovations FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access to articles" ON articles FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access to embeddings" ON embeddings FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access to individuals" ON individuals FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role access to innovation_organizations" ON innovation_organizations FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role access to innovation_individuals" ON innovation_individuals FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role access to publication_authors" ON publication_authors FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role access to publication_organizations" ON publication_organizations FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

CREATE OR REPLACE FUNCTION user_can_access_innovation(innovation_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM innovations WHERE id = innovation_uuid AND visibility = 'public') THEN
        RETURN true;
    END IF;
    
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

CREATE OR REPLACE FUNCTION user_can_moderate()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM individuals 
        WHERE email = auth.jwt() ->> 'email' 
        AND role IN ('admin', 'moderator')
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- TRIGGERS
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS update_organizations_updated_at ON organizations;
DROP TRIGGER IF EXISTS update_individuals_updated_at ON individuals;
DROP TRIGGER IF EXISTS update_publications_updated_at ON publications;
DROP TRIGGER IF EXISTS update_innovations_updated_at ON innovations;
DROP TRIGGER IF EXISTS update_articles_updated_at ON articles;
DROP TRIGGER IF EXISTS update_comments_updated_at ON comments;

-- Create triggers
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_individuals_updated_at BEFORE UPDATE ON individuals FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_publications_updated_at BEFORE UPDATE ON publications FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_innovations_updated_at BEFORE UPDATE ON innovations FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- =====================================================
-- DASHBOARD VIEW
-- =====================================================

DROP MATERIALIZED VIEW IF EXISTS dashboard_stats;

CREATE MATERIALIZED VIEW dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM publications) as total_publications,
    (SELECT COUNT(*) FROM innovations) as total_innovations,
    (SELECT COUNT(*) FROM organizations) as total_organizations,
    (SELECT COUNT(*) FROM individuals WHERE verification_status = 'verified') as verified_individuals,
    (SELECT COUNT(DISTINCT entity) FROM publications, unnest(african_entities) as entity) as african_countries_covered,
    (SELECT COUNT(DISTINCT keyword) FROM publications, unnest(keywords) as keyword) as unique_keywords,
    (SELECT AVG(african_relevance_score) FROM publications WHERE african_relevance_score > 0) as avg_african_relevance,
    (SELECT AVG(ai_relevance_score) FROM publications WHERE ai_relevance_score > 0) as avg_ai_relevance,
    NOW() as last_updated;

CREATE UNIQUE INDEX IF NOT EXISTS dashboard_stats_updated_idx ON dashboard_stats (last_updated);

-- =====================================================
-- INITIAL DATA
-- =====================================================

INSERT INTO organizations (name, organization_type, country, description) 
VALUES 
('University of Cape Town', 'university', 'South Africa', 'Leading research university in South Africa'),
('University of Nairobi', 'university', 'Kenya', 'Premier university in East Africa'),
('Cairo University', 'university', 'Egypt', 'One of Egypt''s premier public universities'),
('AIMS (African Institute for Mathematical Sciences)', 'research_center', 'Multi-country', 'Network of centres of excellence for postgraduate education, research and public engagement in mathematical sciences')
ON CONFLICT DO NOTHING;

-- Success message
SELECT 'TAIFA-FIALA database schema successfully updated with RLS policies!' as result;