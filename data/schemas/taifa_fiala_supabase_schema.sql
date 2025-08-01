-- TAIFA-FIALA Database Schema for Supabase
-- Innovation-focused platform for African AI R&D documentation
-- Based on PRD requirements and unified academic dataset structure

-- =====================================================
-- CORE TABLES FOR INNOVATION DOCUMENTATION
-- =====================================================

-- Organizations table (universities, companies, research centers)
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  organization_type TEXT NOT NULL, -- 'university', 'company', 'research_center', 'government', 'ngo', 'other'
  country TEXT NOT NULL,
  website TEXT,
  description TEXT,
  founded_date DATE,
  contact_email TEXT,
  logo_url TEXT,
  verification_status TEXT DEFAULT 'pending', -- 'pending', 'verified', 'rejected'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individuals table (researchers, innovators, contributors)
CREATE TABLE individuals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  role TEXT, -- 'researcher', 'innovator', 'student', 'policy_maker', 'funder', 'other'
  bio TEXT,
  country TEXT,
  organization_id UUID REFERENCES organizations(id),
  linkedin_url TEXT,
  twitter_url TEXT,
  website_url TEXT,
  orcid_id TEXT,
  profile_image_url TEXT,
  expertise_areas TEXT[], -- Array of expertise areas
  verification_status TEXT DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Publications table (papers, articles, reports)
CREATE TABLE publications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  abstract TEXT,
  publication_type TEXT NOT NULL, -- 'journal_paper', 'conference_paper', 'preprint', 'report', 'thesis', 'other'
  publication_date DATE,
  year INTEGER,
  doi TEXT,
  url TEXT,
  pdf_url TEXT,
  journal TEXT,
  venue TEXT,
  citation_count INTEGER DEFAULT 0,
  
  -- AI/Research Classification
  project_domain TEXT, -- 'healthcare', 'agriculture', 'finance', 'education', etc.
  ai_techniques TEXT, -- Description of AI/ML techniques used
  geographic_scope TEXT, -- Countries or regions covered
  funding_source TEXT,
  key_outcomes TEXT,
  
  -- Relevance Scores (0.0 to 1.0)
  african_relevance_score DECIMAL(3,2) DEFAULT 0.0,
  ai_relevance_score DECIMAL(3,2) DEFAULT 0.0,
  
  -- Metadata
  african_entities TEXT[], -- Array of African countries/regions mentioned
  keywords TEXT[], -- Array of keywords
  source TEXT NOT NULL, -- 'arxiv', 'pubmed', 'google_scholar', 'systematic_review', 'manual'
  source_id TEXT, -- Original ID from source system
  data_type TEXT DEFAULT 'Academic Paper',
  
  -- Processing metadata
  processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  verification_status TEXT DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Innovations table (AI projects, solutions, products)
CREATE TABLE innovations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  innovation_type TEXT NOT NULL, -- 'software', 'hardware', 'service', 'methodology', 'dataset', 'other'
  
  -- Classification
  domain TEXT NOT NULL, -- 'healthcare', 'agriculture', 'finance', 'education', etc.
  ai_techniques_used TEXT[],
  target_beneficiaries TEXT,
  problem_addressed TEXT,
  solution_approach TEXT,
  
  -- Development details
  development_stage TEXT DEFAULT 'concept', -- 'concept', 'prototype', 'pilot', 'production', 'scaled'
  technology_stack TEXT[],
  programming_languages TEXT[],
  datasets_used TEXT[],
  
  -- Geographic and impact
  countries_deployed TEXT[],
  target_countries TEXT[],
  users_reached INTEGER DEFAULT 0,
  impact_metrics JSONB,
  
  -- Verification and visibility
  verification_status TEXT DEFAULT 'pending', -- 'pending', 'community_verified', 'expert_verified'
  visibility TEXT DEFAULT 'public', -- 'public', 'private', 'restricted'
  
  -- Media and documentation
  demo_url TEXT,
  github_url TEXT,
  documentation_url TEXT,
  video_url TEXT,
  image_urls TEXT[],
  
  -- Metadata
  creation_date DATE,
  last_updated_date DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fundings table (grants, investments, awards)
CREATE TABLE fundings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  innovation_id UUID REFERENCES innovations(id),
  funder_org_id UUID REFERENCES organizations(id),
  funding_type TEXT NOT NULL, -- 'grant', 'investment', 'award', 'contract', 'donation', 'other'
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

-- =====================================================
-- RELATIONSHIP TABLES
-- =====================================================

-- Innovation-Organization relationships
CREATE TABLE innovation_organizations (
  innovation_id UUID REFERENCES innovations(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  relationship_type TEXT NOT NULL, -- 'developer', 'collaborator', 'funder', 'user', 'partner'
  role_description TEXT,
  start_date DATE,
  end_date DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (innovation_id, organization_id, relationship_type)
);

-- Innovation-Individual relationships
CREATE TABLE innovation_individuals (
  innovation_id UUID REFERENCES innovations(id) ON DELETE CASCADE,
  individual_id UUID REFERENCES individuals(id) ON DELETE CASCADE,
  relationship_type TEXT NOT NULL, -- 'lead_developer', 'contributor', 'researcher', 'advisor', 'user'
  role_description TEXT,
  contribution_details TEXT,
  start_date DATE,
  end_date DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (innovation_id, individual_id, relationship_type)
);

-- Innovation-Publication relationships
CREATE TABLE innovation_publications (
  innovation_id UUID REFERENCES innovations(id) ON DELETE CASCADE,
  publication_id UUID REFERENCES publications(id) ON DELETE CASCADE,
  relationship_type TEXT NOT NULL, -- 'describes', 'evaluates', 'uses', 'cites', 'extends'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (innovation_id, publication_id)
);

-- Publication-Individual relationships (authorship)
CREATE TABLE publication_authors (
  publication_id UUID REFERENCES publications(id) ON DELETE CASCADE,
  individual_id UUID REFERENCES individuals(id) ON DELETE CASCADE,
  author_order INTEGER,
  affiliation TEXT,
  corresponding_author BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (publication_id, individual_id)
);

-- Publication-Organization relationships (affiliations)
CREATE TABLE publication_organizations (
  publication_id UUID REFERENCES publications(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  relationship_type TEXT DEFAULT 'affiliation', -- 'affiliation', 'funder', 'publisher'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (publication_id, organization_id)
);

-- =====================================================
-- VECTOR STORAGE INTEGRATION
-- =====================================================

-- Embeddings table (for Pinecone integration)
CREATE TABLE embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_type TEXT NOT NULL, -- 'innovation', 'publication', 'organization', 'individual'
  source_id UUID NOT NULL,
  vector_id TEXT NOT NULL, -- Pinecone vector ID
  embedding_model TEXT DEFAULT 'sentence-transformers', -- Model used for embedding
  vector_dimension INTEGER DEFAULT 384,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- CONTENT MANAGEMENT AND COMMUNITY
-- =====================================================

-- News and articles table (RSS and community content)
CREATE TABLE articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT,
  summary TEXT,
  url TEXT,
  source_name TEXT,
  source_type TEXT, -- 'rss', 'manual', 'scraping'
  article_type TEXT DEFAULT 'news', -- 'news', 'blog', 'announcement', 'case_study'
  
  -- Classification
  topics TEXT[],
  countries_mentioned TEXT[],
  organizations_mentioned TEXT[],
  
  -- Metadata
  published_date TIMESTAMP WITH TIME ZONE,
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  author TEXT,
  image_url TEXT,
  
  -- Relevance
  african_relevance_score DECIMAL(3,2) DEFAULT 0.0,
  ai_relevance_score DECIMAL(3,2) DEFAULT 0.0,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Comments and community engagement
CREATE TABLE comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content TEXT NOT NULL,
  parent_id UUID REFERENCES comments(id), -- For nested comments
  
  -- Polymorphic references (what is being commented on)
  target_type TEXT NOT NULL, -- 'innovation', 'publication', 'article', 'organization'
  target_id UUID NOT NULL,
  
  -- Author (can be individual or anonymous)
  author_id UUID REFERENCES individuals(id),
  author_name TEXT, -- For anonymous comments
  author_email TEXT,
  
  -- Moderation
  status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'hidden'
  moderated_by UUID REFERENCES individuals(id),
  moderated_at TIMESTAMP WITH TIME ZONE,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ratings and reviews
CREATE TABLE ratings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- What is being rated
  target_type TEXT NOT NULL, -- 'innovation', 'publication', 'organization'
  target_id UUID NOT NULL,
  
  -- Rating details
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  review_text TEXT,
  criteria JSONB, -- Structured rating criteria
  
  -- Rater
  rater_id UUID REFERENCES individuals(id),
  rater_expertise TEXT,
  
  -- Verification
  verified_rating BOOLEAN DEFAULT FALSE,
  verification_method TEXT,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Ensure one rating per person per item
  UNIQUE(target_type, target_id, rater_id)
);

-- =====================================================
-- LEGACY DATA ARCHIVE
-- =====================================================

-- Archive for original funding announcements (if any legacy data exists)
CREATE TABLE legacy_funding_announcements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  original_data JSONB NOT NULL,
  source_system TEXT,
  archived_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  migrated_to_innovation_id UUID REFERENCES innovations(id),
  migration_notes TEXT
);

-- =====================================================
-- SYSTEM TABLES
-- =====================================================

-- Data ingestion logs
CREATE TABLE ingestion_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_type TEXT NOT NULL, -- 'arxiv', 'pubmed', 'google_scholar', 'rss', 'manual'
  status TEXT NOT NULL, -- 'started', 'completed', 'failed'
  records_processed INTEGER DEFAULT 0,
  records_inserted INTEGER DEFAULT 0,
  records_updated INTEGER DEFAULT 0,
  error_message TEXT,
  processing_time_seconds INTEGER,
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE
);

-- User sessions and activity (for analytics)
CREATE TABLE user_sessions (
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
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Text search indexes
CREATE INDEX idx_publications_title_search ON publications USING gin(to_tsvector('english', title));
CREATE INDEX idx_publications_abstract_search ON publications USING gin(to_tsvector('english', abstract));
CREATE INDEX idx_innovations_title_search ON innovations USING gin(to_tsvector('english', title));
CREATE INDEX idx_innovations_description_search ON innovations USING gin(to_tsvector('english', description));
CREATE INDEX idx_organizations_name_search ON organizations USING gin(to_tsvector('english', name));

-- Array indexes for keyword searches
CREATE INDEX idx_publications_keywords ON publications USING gin(keywords);
CREATE INDEX idx_publications_african_entities ON publications USING gin(african_entities);
CREATE INDEX idx_innovations_ai_techniques ON innovations USING gin(ai_techniques_used);
CREATE INDEX idx_innovations_countries ON innovations USING gin(countries_deployed);

-- Performance indexes
CREATE INDEX idx_publications_year ON publications(year);
CREATE INDEX idx_publications_african_score ON publications(african_relevance_score);
CREATE INDEX idx_publications_ai_score ON publications(ai_relevance_score);
CREATE INDEX idx_publications_source ON publications(source);
CREATE INDEX idx_innovations_domain ON innovations(domain);
CREATE INDEX idx_innovations_verification_status ON innovations(verification_status);
CREATE INDEX idx_organizations_country ON organizations(country);
CREATE INDEX idx_individuals_country ON individuals(country);

-- Compound indexes for common queries
CREATE INDEX idx_publications_african_ai_scores ON publications(african_relevance_score, ai_relevance_score);
CREATE INDEX idx_publications_year_source ON publications(year, source);
CREATE INDEX idx_innovations_domain_stage ON innovations(domain, development_stage);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on ALL tables
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
-- PUBLIC READ POLICIES (Anonymous + Authenticated)
-- =====================================================

-- Organizations - Public read access
CREATE POLICY "Public read access for organizations" ON organizations 
FOR SELECT USING (true);

-- Publications - Public read access  
CREATE POLICY "Public read access for publications" ON publications 
FOR SELECT USING (true);

-- Innovations - Public read for public innovations only
CREATE POLICY "Public read access for public innovations" ON innovations 
FOR SELECT USING (visibility = 'public');

-- Articles - Public read access
CREATE POLICY "Public read access for articles" ON articles 
FOR SELECT USING (true);

-- Embeddings - Public read access (needed for search)
CREATE POLICY "Public read access for embeddings" ON embeddings 
FOR SELECT USING (true);

-- Relationship tables - Public read access (for public data connections)
CREATE POLICY "Public read for innovation_organizations" ON innovation_organizations 
FOR SELECT USING (
  innovation_id IN (SELECT id FROM innovations WHERE visibility = 'public')
);

CREATE POLICY "Public read for innovation_publications" ON innovation_publications 
FOR SELECT USING (true);

CREATE POLICY "Public read for publication_authors" ON publication_authors 
FOR SELECT USING (true);

CREATE POLICY "Public read for publication_organizations" ON publication_organizations 
FOR SELECT USING (true);

-- =====================================================
-- INDIVIDUAL/USER PRIVACY POLICIES
-- =====================================================

-- Individuals - Privacy controls
CREATE POLICY "Public read for verified individuals" ON individuals 
FOR SELECT USING (verification_status = 'verified');

CREATE POLICY "Users can read their own data" ON individuals 
FOR SELECT USING (auth.uid()::text = email);

CREATE POLICY "Users can update their own data" ON individuals 
FOR UPDATE USING (auth.uid()::text = email);

-- Innovation_individuals - Privacy for user connections
CREATE POLICY "Public read for verified individual connections" ON innovation_individuals 
FOR SELECT USING (
  individual_id IN (SELECT id FROM individuals WHERE verification_status = 'verified')
  AND innovation_id IN (SELECT id FROM innovations WHERE visibility = 'public')
);

CREATE POLICY "Users can read their own innovation connections" ON innovation_individuals 
FOR SELECT USING (
  individual_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email')
);

-- =====================================================
-- CONTENT CREATION AND MODERATION POLICIES
-- =====================================================

-- Comments - Moderated content
CREATE POLICY "Public read approved comments" ON comments 
FOR SELECT USING (status = 'approved');

CREATE POLICY "Users can read their own comments" ON comments 
FOR SELECT USING (
  author_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email')
);

CREATE POLICY "Authenticated users can create comments" ON comments 
FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Users can update their own comments" ON comments 
FOR UPDATE USING (
  author_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email')
);

-- Ratings - User reviews
CREATE POLICY "Public read for ratings" ON ratings 
FOR SELECT USING (true);

CREATE POLICY "Authenticated users can create ratings" ON ratings 
FOR INSERT WITH CHECK (
  auth.role() = 'authenticated' 
  AND rater_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email')
);

CREATE POLICY "Users can update their own ratings" ON ratings 
FOR UPDATE USING (
  rater_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email')
);

-- =====================================================
-- CONTENT MANAGEMENT POLICIES
-- =====================================================

-- Innovations - Content creation and updates
CREATE POLICY "Authenticated users can create innovations" ON innovations 
FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Users can update innovations they're connected to" ON innovations 
FOR UPDATE USING (
  id IN (
    SELECT innovation_id FROM innovation_individuals 
    WHERE individual_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email')
    AND relationship_type IN ('lead_developer', 'contributor')
  )
);

-- Fundings - Financial information
CREATE POLICY "Public read for verified fundings" ON fundings 
FOR SELECT USING (verified = true);

CREATE POLICY "Authenticated users can create funding records" ON fundings 
FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- =====================================================
-- ADMIN AND SYSTEM POLICIES
-- =====================================================

-- Ingestion logs - System access only
CREATE POLICY "Service role access for ingestion logs" ON ingestion_logs 
FOR ALL USING (auth.role() = 'service_role');

-- User sessions - Privacy protected
CREATE POLICY "Users can read their own sessions" ON user_sessions 
FOR SELECT USING (
  user_id IN (SELECT id FROM individuals WHERE email = auth.jwt() ->> 'email')
);

CREATE POLICY "System can manage user sessions" ON user_sessions 
FOR ALL USING (auth.role() = 'service_role');

-- Legacy data - Public read only
CREATE POLICY "Public read for legacy data" ON legacy_funding_announcements 
FOR SELECT USING (true);

-- =====================================================
-- SERVICE ROLE POLICIES (For ETL and Admin Operations)
-- =====================================================

-- Allow service role to manage all data (for ETL processes)
CREATE POLICY "Service role full access to organizations" ON organizations 
FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to publications" ON publications 
FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to innovations" ON innovations 
FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to articles" ON articles 
FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to embeddings" ON embeddings 
FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to individuals" ON individuals 
FOR ALL USING (auth.role() = 'service_role');

-- Relationship tables - Service role access
CREATE POLICY "Service role access to innovation_organizations" ON innovation_organizations 
FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role access to innovation_individuals" ON innovation_individuals 
FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role access to publication_authors" ON publication_authors 
FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role access to publication_organizations" ON publication_organizations 
FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- POLICY HELPER FUNCTIONS
-- =====================================================

-- Function to check if user owns or contributes to innovation
CREATE OR REPLACE FUNCTION user_can_access_innovation(innovation_uuid UUID)
RETURNS BOOLEAN AS $$
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

-- Function to check if user can moderate content
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
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_individuals_updated_at BEFORE UPDATE ON individuals FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_publications_updated_at BEFORE UPDATE ON publications FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_innovations_updated_at BEFORE UPDATE ON innovations FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Function to calculate innovation metrics
CREATE OR REPLACE FUNCTION calculate_innovation_metrics(innovation_uuid UUID)
RETURNS JSONB AS $$
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

-- =====================================================
-- INITIAL DATA AND CONFIGURATIONS
-- =====================================================

-- Insert some initial organization types and domains
INSERT INTO organizations (name, organization_type, country, description) VALUES
('University of Cape Town', 'university', 'South Africa', 'Leading research university in South Africa'),
('University of Nairobi', 'university', 'Kenya', 'Premier university in East Africa'),
('Cairo University', 'university', 'Egypt', 'One of Egypt''s premier public universities'),
('AIMS (African Institute for Mathematical Sciences)', 'research_center', 'Multi-country', 'Network of centres of excellence for postgraduate education, research and public engagement in mathematical sciences');

-- Create materialized view for dashboard statistics
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

CREATE UNIQUE INDEX ON dashboard_stats (last_updated);

-- =====================================================
-- COMMENTS AND DOCUMENTATION
-- =====================================================

COMMENT ON TABLE publications IS 'Academic publications, papers, and research outputs';
COMMENT ON TABLE innovations IS 'AI innovations, projects, and solutions developed in Africa';
COMMENT ON TABLE organizations IS 'Universities, companies, and institutions involved in African AI';
COMMENT ON TABLE individuals IS 'Researchers, innovators, and contributors to African AI';
COMMENT ON TABLE fundings IS 'Funding sources and financial support for innovations';
COMMENT ON TABLE embeddings IS 'Vector embeddings for semantic search via Pinecone';
COMMENT ON TABLE articles IS 'News articles, blog posts, and community content';
COMMENT ON TABLE ingestion_logs IS 'Logs of automated data ingestion from various sources';

COMMENT ON COLUMN publications.african_relevance_score IS 'Score 0.0-1.0 indicating relevance to Africa';
COMMENT ON COLUMN publications.ai_relevance_score IS 'Score 0.0-1.0 indicating AI/ML content relevance';
COMMENT ON COLUMN innovations.verification_status IS 'Community or expert verification of innovation claims';
COMMENT ON COLUMN innovations.visibility IS 'Controls public visibility of innovation details';

-- Grant permissions for application user
-- (These would be configured in Supabase dashboard or via service role)
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;