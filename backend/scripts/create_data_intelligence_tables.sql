-- Data Intelligence Database Schema
-- Tables to support citation analysis, enhanced publication metadata, and competitive intelligence

-- Citation relationships table
CREATE TABLE IF NOT EXISTS citation_relationships (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    citing_paper_id UUID REFERENCES publications(id),
    cited_paper_id UUID REFERENCES publications(id),
    citation_context TEXT,
    confidence_score FLOAT DEFAULT 0.0,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Author affiliations table
CREATE TABLE IF NOT EXISTS author_affiliations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    author_name VARCHAR(255) NOT NULL,
    institution VARCHAR(500),
    country VARCHAR(100),
    department VARCHAR(500),
    confidence FLOAT DEFAULT 0.0,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Institutional connections table
CREATE TABLE IF NOT EXISTS institutional_connections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    institution_1 VARCHAR(500) NOT NULL,
    institution_2 VARCHAR(500) NOT NULL,
    connection_type VARCHAR(100), -- "collaboration", "author_movement", "citation"
    strength FLOAT DEFAULT 0.0,
    evidence JSONB DEFAULT '[]'::jsonb,
    identified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge flows table (research to innovation)
CREATE TABLE IF NOT EXISTS knowledge_flows (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source_publication_id UUID REFERENCES publications(id),
    target_innovation_id UUID REFERENCES innovations(id),
    flow_strength FLOAT DEFAULT 0.0,
    intermediate_nodes JSONB DEFAULT '[]'::jsonb,
    time_to_market_days INTEGER,
    transformation_type VARCHAR(50), -- "direct", "evolved", "combined"
    mapped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add columns to existing publications table for enhanced metadata
DO $$
BEGIN
    -- Development stage information
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'publications' AND column_name = 'development_stage') THEN
        ALTER TABLE publications ADD COLUMN development_stage VARCHAR(50);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'publications' AND column_name = 'stage_confidence') THEN
        ALTER TABLE publications ADD COLUMN stage_confidence FLOAT DEFAULT 0.0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'publications' AND column_name = 'stage_indicators') THEN
        ALTER TABLE publications ADD COLUMN stage_indicators JSONB DEFAULT '[]'::jsonb;
    END IF;
    
    -- Business model information
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'publications' AND column_name = 'business_model') THEN
        ALTER TABLE publications ADD COLUMN business_model VARCHAR(50);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'publications' AND column_name = 'business_model_confidence') THEN
        ALTER TABLE publications ADD COLUMN business_model_confidence FLOAT DEFAULT 0.0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'publications' AND column_name = 'target_markets') THEN
        ALTER TABLE publications ADD COLUMN target_markets JSONB DEFAULT '[]'::jsonb;
    END IF;
    
    -- Technology extraction
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'publications' AND column_name = 'extracted_technologies') THEN
        ALTER TABLE publications ADD COLUMN extracted_technologies JSONB DEFAULT '[]'::jsonb;
    END IF;
    
    -- Impact metrics (if not already exists)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'publications' AND column_name = 'impact_metrics') THEN
        ALTER TABLE publications ADD COLUMN impact_metrics JSONB DEFAULT '{}'::jsonb;
    END IF;
END $$;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_citation_relationships_citing ON citation_relationships(citing_paper_id);
CREATE INDEX IF NOT EXISTS idx_citation_relationships_cited ON citation_relationships(cited_paper_id);
CREATE INDEX IF NOT EXISTS idx_citation_relationships_confidence ON citation_relationships(confidence_score);

CREATE INDEX IF NOT EXISTS idx_author_affiliations_author ON author_affiliations(author_name);
CREATE INDEX IF NOT EXISTS idx_author_affiliations_institution ON author_affiliations(institution);
CREATE INDEX IF NOT EXISTS idx_author_affiliations_country ON author_affiliations(country);

CREATE INDEX IF NOT EXISTS idx_institutional_connections_inst1 ON institutional_connections(institution_1);
CREATE INDEX IF NOT EXISTS idx_institutional_connections_inst2 ON institutional_connections(institution_2);
CREATE INDEX IF NOT EXISTS idx_institutional_connections_type ON institutional_connections(connection_type);

CREATE INDEX IF NOT EXISTS idx_knowledge_flows_source ON knowledge_flows(source_publication_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_flows_target ON knowledge_flows(target_innovation_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_flows_strength ON knowledge_flows(flow_strength);

CREATE INDEX IF NOT EXISTS idx_publications_development_stage ON publications(development_stage);
CREATE INDEX IF NOT EXISTS idx_publications_business_model ON publications(business_model);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_citation_relationships_composite ON citation_relationships(citing_paper_id, cited_paper_id, confidence_score);
CREATE INDEX IF NOT EXISTS idx_author_affiliations_composite ON author_affiliations(author_name, institution, country);

-- Views for analytics
CREATE OR REPLACE VIEW publication_citation_counts AS
SELECT 
    p.id,
    p.title,
    p.publication_date,
    COUNT(cr.citing_paper_id) as citation_count,
    AVG(cr.confidence_score) as avg_citation_confidence
FROM publications p
LEFT JOIN citation_relationships cr ON p.id = cr.cited_paper_id
GROUP BY p.id, p.title, p.publication_date;

CREATE OR REPLACE VIEW institutional_collaboration_matrix AS
SELECT 
    ic.institution_1,
    ic.institution_2,
    ic.connection_type,
    COUNT(*) as connection_count,
    AVG(ic.strength) as avg_strength
FROM institutional_connections ic
GROUP BY ic.institution_1, ic.institution_2, ic.connection_type;

CREATE OR REPLACE VIEW research_to_innovation_pipeline AS
SELECT 
    p.id as publication_id,
    p.title as publication_title,
    p.publication_date,
    i.id as innovation_id,
    i.title as innovation_title,
    i.creation_date,
    kf.flow_strength,
    kf.time_to_market_days,
    kf.transformation_type
FROM knowledge_flows kf
JOIN publications p ON kf.source_publication_id = p.id
JOIN innovations i ON kf.target_innovation_id = i.id
ORDER BY kf.flow_strength DESC;

-- Comments for documentation
COMMENT ON TABLE citation_relationships IS 'Extracted citation relationships between publications';
COMMENT ON TABLE author_affiliations IS 'Author institutional affiliations extracted from publications';
COMMENT ON TABLE institutional_connections IS 'Connections and collaborations between institutions';
COMMENT ON TABLE knowledge_flows IS 'Knowledge transfer paths from research publications to innovations';

COMMENT ON COLUMN publications.development_stage IS 'Detected development stage: research, prototype, pilot, scaling, commercial';
COMMENT ON COLUMN publications.business_model IS 'Detected business model: B2B, B2C, B2G, NGO, research';
COMMENT ON COLUMN publications.target_markets IS 'Identified target markets and application domains';
COMMENT ON COLUMN publications.extracted_technologies IS 'Technologies and methods extracted from publication content';
COMMENT ON COLUMN publications.impact_metrics IS 'Calculated impact metrics including citation counts and influence scores';