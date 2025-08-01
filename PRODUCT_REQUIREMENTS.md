# PRODUCT REQUIREMENTS DOCUMENT

# Product Requirements Document: TAIFA-FIALA Platform Refactoring

## 1. Introduction

### 1.1 Purpose

This Product Requirements Document (PRD) outlines the comprehensive plan for refactoring the TAIFA-FIALA platform from a funding tracker to an innovation archive. The document serves as a guide for developers, stakeholders, and AI assistance in implementing the strategic restructuring plan.

### 1.2 Product Vision

Transform TAIFA-FIALA from a passive funding announcement aggregator to an active innovation-driven research platform that documents African AI excellence, creating a unified space where funders showcase impact, innovators gain recognition, and researchers access rigorous evidence.

### 1.3 Scope

The refactoring will involve a complete overhaul of the existing codebase in a new repository, maintaining the technology stack foundations while redesigning the architecture, database schema, and user experience to align with the new strategic direction.

## 2. Technical Architecture

### 2.1 Repository Structure

Create a new GitHub repository with the following structure:

```bash
taifa-fiala-innovation-archive/
├── .github/
│   └── workflows/              # CI/CD pipelines
├── frontend/                   # Next.js application
│   ├── components/             # React components
│   ├── app/                    # Next.js 15 App Router
│   ├── public/                 # Static assets
│   ├── styles/                 # CSS/SCSS files
│   └── utils/                  # Utility functions
├── backend/
│   ├── api/                    # FastAPI endpoints
│   ├── etl/                    # Data extraction, transformation, loading
│   │   ├── academic/           # Academic publication mining
│   │   ├── news/               # News monitoring
│   │   └── community/          # Community contributions
│   ├── models/                 # Data models
│   └── services/               # Business logic
├── data/
│   ├── schemas/                # Database schemas
│   ├── migrations/             # Database migrations
│   └── seed/                   # Seed data
├── docs/
│   ├── api/                    # API documentation
│   ├── architecture/           # Architecture diagrams
│   └── methodology/            # Research methodology
└── scripts/                    # Utility scripts

```

### 2.2 Technology Stack

- **Frontend:** Next.js with React, maintaining the original theme but completely reworking the content
- **Backend:** Python FastAPI, redesigned from scratch to focus on AI projects and innovations
- **Databases:** Supabase (relational), Pinecone (vector)
- **ETL:** Custom Python modules for academic publication mining, news monitoring, and community contributions
- **Search:** Integration with serper.dev for precision searches and Crawl4AI for project site extraction
- **Authentication:** OAuth 2.0 with Supabase Auth
- **Deployment:** Vercel (frontend), Docker containers on AWS or GCP (backend)

### 2.3 Data Model Redesign

Completely scrap the existing schema and design a new one focused on innovations rather than funding announcements:

```sql
-- Core Tables
CREATE TABLE innovations (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  innovation_type TEXT NOT NULL,
  creation_date DATE,
  verification_status TEXT NOT NULL,
  visibility TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE organizations (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  organization_type TEXT NOT NULL,
  country TEXT NOT NULL,
  website TEXT,
  founded_date DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE individuals (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT,
  role TEXT,
  bio TEXT,
  country TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE fundings (
  id UUID PRIMARY KEY,
  innovation_id UUID REFERENCES innovations(id),
  funder_org_id UUID REFERENCES organizations(id),
  amount DECIMAL,
  currency TEXT,
  funding_date DATE,
  funding_type TEXT,
  verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE publications (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  publication_type TEXT NOT NULL,
  publication_date DATE,
  doi TEXT,
  url TEXT,
  journal TEXT,
  abstract TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Relationship Tables
CREATE TABLE innovation_organizations (
  innovation_id UUID REFERENCES innovations(id),
  organization_id UUID REFERENCES organizations(id),
  relationship_type TEXT NOT NULL,
  PRIMARY KEY (innovation_id, organization_id)
);

CREATE TABLE innovation_individuals (
  innovation_id UUID REFERENCES innovations(id),
  individual_id UUID REFERENCES individuals(id),
  relationship_type TEXT NOT NULL,
  PRIMARY KEY (innovation_id, individual_id)
);

CREATE TABLE innovation_publications (
  innovation_id UUID REFERENCES innovations(id),
  publication_id UUID REFERENCES publications(id),
  relationship_type TEXT NOT NULL,
  PRIMARY KEY (innovation_id, publication_id)
);

-- Vector Store Integration
CREATE TABLE embeddings (
  id UUID PRIMARY KEY,
  source_type TEXT NOT NULL,
  source_id UUID NOT NULL,
  vector_id TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Legacy Data Archive
CREATE TABLE legacy_funding_announcements (
  id UUID PRIMARY KEY,
  original_data JSONB NOT NULL,
  archived_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

```

## 3. Core Features

### 3.1 Innovation Documentation System

- **Innovation Profile Creation:** Enable users to document AI innovations with standardized metadata
- **Evidence Collection:** Support multiple evidence types (publications, demos, testimonials)
- **Verification Framework:** Multi-tiered verification system with community and expert validation
- **Impact Tracking:** Longitudinal documentation of innovation outcomes and developments

### 3.2 Systematic Literature Foundation

- **Academic Publication Mining:** ETL pipeline for extracting AI innovation data from journals
- **Signal Intelligence Collection:** Automated monitoring of digital platforms for innovation signals
- **Systematic Review Protocols:** Standardized data extraction and classification
- **Network Analysis:** Tools for mapping collaboration patterns in African AI research

### 3.3 Community Engagement Platform

- **Innovator Profiles:** Dedicated spaces for innovators to showcase their work
- **Annotation System:** Enable community contribution to innovation documentation
- **Peer Review Mechanism:** Community-driven validation of innovation claims
- **Three-Tier Participation:** Scalable engagement options for different stakeholder capacities

### 3.4 Living Review Platform

- **Real-Time Evidence Integration:** Systems for continuous updating of innovation documentation
- **Collaboration Facilitation:** Tools to connect innovators, funders, and researchers
- **Longitudinal Tracking:** Framework for monitoring innovation trajectories over time
- **Participatory Meta-Analysis:** Tools for community input on data interpretation

### 3.5 Legacy Data Integration

- **Funding Announcement Archive:** Preserve existing data in searchable format
- **Migration Pathway:** Connect relevant funding announcements to documented innovations
- **Semantic Search:** Make archived data accessible through natural language queries

## 4. User Personas and Journeys

### 4.1 Key User Personas

- **AI Innovator**
    
    African entrepreneurs, researchers, or developers creating AI solutions seeking recognition, connections, and resources.
    
    **Primary Goals:**
    
    - Document their innovation for visibility and credibility
    - Connect with potential funders and collaborators
    - Access relevant research and development insights
- **Funder**
    
    Organizations or individuals providing financial support to African AI initiatives seeking to showcase impact and identify promising innovations.
    
    **Primary Goals:**
    
    - Highlight successful investments and their outcomes
    - Discover high-potential innovations for funding consideration
    - Access evidence-based insights for strategic decision-making
- **Researcher**
    
    Academic or industry professionals studying African AI development seeking comprehensive, reliable data.
    
    **Primary Goals:**
    
    - Access rigorous, systematic evidence on African AI innovation
    - Contribute to participatory meta-analysis and interpretation
    - Connect research findings to real-world applications
- **Policy Maker**
    
    Government officials or organizational leaders shaping AI policy and investment strategies.
    
    **Primary Goals:**
    
    - Access evidence-based insights for policy formulation
    - Identify trends and gaps in the innovation ecosystem
    - Evaluate the impact of existing policies and investments

### 4.2 Key User Journeys

- **Innovation Documentation Journey**
    
    **User:** AI Innovator
    
    **Journey Steps:**
    
    1. Discovers platform through systematic outreach or ecosystem connections
    2. Creates account and claims profile (if innovation already detected in systematic review)
    3. Documents innovation with standardized metadata and supporting evidence
    4. Participates in verification process through community validation
    5. Receives recognition, connects with potential collaborators, and tracks impact
- **Funding Impact Showcase Journey**
    
    **User:** Funder
    
    **Journey Steps:**
    
    1. Creates organizational profile with funding focus areas
    2. Links to innovations supported through their funding
    3. Provides verification of funding claims by innovators
    4. Showcases portfolio impact through aggregated innovation outcomes
    5. Discovers new potential funding opportunities through platform recommendations
- **Research Evidence Synthesis Journey**
    
    **User:** Researcher
    
    **Journey Steps:**
    
    1. Accesses systematic literature foundation through research portal
    2. Explores network analysis visualizations of African AI ecosystem
    3. Contributes to participatory meta-analysis of innovation patterns
    4. Publishes findings with citations to platform data
    5. Connects research insights to policy and practice recommendations

## 5. Development Roadmap

### 5.1 Phase 1: Foundation Building (Q3-Q4 2025)

- **Repository setup:** Establish new GitHub repository with CI/CD workflows
- **Database schema implementation:** Deploy new innovation-focused data model
- **ETL pipeline development:** Build academic publication mining framework
- **Legacy data migration:** Archive existing funding announcement data
- **Minimal viable frontend:** Deploy basic Next.js application with core viewing functionality
- **API development:** Create foundational FastAPI endpoints

### 5.2 Phase 2: Core Features Development (Q1-Q2 2026)

- **Innovation documentation system:** Implement standardized profiles and evidence collection
- **Verification framework:** Build multi-tiered validation mechanisms
- **Community features:** Develop user profiles and contribution tools
- **Search and discovery:** Implement semantic search across innovations and evidence
- **Network analysis tools:** Build visualization features for collaboration patterns

### 5.3 Phase 3: Advanced Features (Q3-Q4 2026)

- **Living review infrastructure:** Develop real-time evidence integration
- **Longitudinal tracking:** Implement systems for monitoring innovation trajectories
- **Participatory meta-analysis:** Build collaborative interpretation tools
- **Advanced visualization:** Create interactive dashboards for ecosystem insights
- **API ecosystem:** Develop comprehensive API for external researchers

### 5.4 Phase 4: Scaling and Optimization (2027+)

- **Performance optimization:** Enhance system for increased data volume
- **Methodology extensibility:** Adapt system for other technology domains
- **Predictive analytics:** Implement trend identification capabilities
- **Policy recommendation engine:** Build evidence synthesis for strategic planning
- **Subscription and partnership infrastructure:** Develop sustainable funding model

## 6. AI-Specific Development Guidelines

### 6.1 Code Architecture for AI Collaboration

Structure the codebase to facilitate effective AI pair programming:

- **Modular Components:** Break functionality into discrete, well-documented modules
- **Consistent Patterns:** Use consistent coding patterns across the codebase
- **Comprehensive Comments:** Include detailed docstrings and comments explaining intent
- **Type Annotations:** Use Python type hints and TypeScript types for all code
- **Test-Driven Development:** Write tests that clearly express expected behavior

### 6.2 Documentation Standards

Maintain comprehensive documentation to support AI understanding:

- **Architecture Diagrams:** Visualize system components and their relationships
- **API Documentation:** Document all endpoints with OpenAPI specifications
- **Code Examples:** Provide implementation examples for common patterns
- **Development Guides:** Create guides for each major subsystem
- **Decision Records:** Document architectural decisions and their rationales

### 6.3 Data Processing Pipeline Guidelines

Design ETL processes for AI assistance in data extraction and transformation:

- **Step-by-Step Processing:** Break complex ETL into discrete, documentable steps
- **Validation Rules:** Define explicit validation criteria for each data type
- **Error Handling:** Implement comprehensive error handling with clear feedback
- **Sample Data:** Provide representative sample datasets for each pipeline
- **Transformation Templates:** Create templates for common transformation patterns

### 6.4 AI Integration Points

Identify specific system components where AI can provide the most value:

- **Content Extraction:** Extracting structured data from unstructured text
- **Entity Recognition:** Identifying innovations, organizations, and individuals
- **Relationship Mapping:** Detecting connections between ecosystem entities
- **Similarity Detection:** Identifying duplicate or related innovations
- **Content Summarization:** Creating concise descriptions of innovations
- **Classification:** Categorizing innovations by type, sector, and application

## 7. Quality Assurance

### 7.1 Testing Strategy

- **Unit Testing:** Test individual components with pytest (backend) and Jest (frontend)
- **Integration Testing:** Test component interactions with realistic data flows
- **End-to-End Testing:** Validate complete user journeys with Cypress
- **Data Validation Testing:** Verify data integrity across transformations
- **Performance Testing:** Benchmark system performance under various loads

### 7.2 Quality Metrics

- **Code Coverage:** Maintain minimum 80% test coverage across codebase
- **Data Accuracy:** Implement verification protocols for all extracted data
- **Response Time:** Ensure API endpoints respond within 200ms
- **UI Performance:** Maintain Core Web Vitals metrics within recommended ranges
- **Accessibility:** Comply with WCAG 2.1 AA standards

### 7.3 Continuous Integration

- **Automated Testing:** Run test suite on every pull request
- **Code Quality Checks:** Enforce linting, formatting, and complexity rules
- **Security Scanning:** Check dependencies for vulnerabilities
- **Performance Monitoring:** Track performance metrics across deployments
- **Documentation Verification:** Ensure documentation stays in sync with code

## 8. Implementation Considerations

### 8.1 Migration Strategy

Approach for transitioning from the existing system to the new platform:

- **Data Preservation:** Archive all existing funding data before migration
- **Parallel Development:** Build new system while maintaining existing platform
- **Phased Transition:** Gradually shift users to new platform with feature parity
- **Legacy API Support:** Maintain compatibility for existing integrations
- **Comprehensive Communication:** Keep users informed throughout transition

### 8.2 Scalability Considerations

- **Database Partitioning:** Design for horizontal scaling of data storage
- **Caching Strategy:** Implement multi-level caching for frequent queries
- **Asynchronous Processing:** Use message queues for background tasks
- **API Rate Limiting:** Implement fair usage policies for external consumers
- **Content Delivery Network:** Distribute static assets globally

### 8.3 Security Requirements

- **Authentication:** Implement OAuth 2.0 with multi-factor authentication option
- **Authorization:** Fine-grained permission system for different user roles
- **Data Encryption:** Encrypt sensitive data at rest and in transit
- **Input Validation:** Validate all user inputs to prevent injection attacks
- **Regular Security Audits:** Conduct periodic security reviews

## 9. Success Metrics

### 9.1 Technical Performance Metrics

- **System Reliability:** 99.9% uptime for production environment
- **Data Processing Efficiency:** ETL pipeline processing times and accuracy
- **Search Performance:** Query response times and relevance scores
- **API Usage:** Endpoint utilization and response times
- **Database Performance:** Query execution times and optimization metrics

### 9.2 User Engagement Metrics

- **Innovation Documentation:** Number of innovations documented and verified
- **Community Participation:** Active users contributing to platform content
- **Research Utilization:** Citations and references to platform data
- **Stakeholder Satisfaction:** User satisfaction scores across persona types
- **Platform Influence:** Evidence of platform data influencing decisions

### 9.3 Academic Impact Metrics

- **Methodological Adoption:** Other initiatives implementing similar approaches
- **Publication Citations:** Academic references to platform methodology
- **Dataset Usage:** External research utilizing platform data
- **Collaboration Networks:** Research partnerships facilitated through platform
- **Evidence-Based Recommendations:** Policy changes informed by platform insights

## 10. Conclusion

This PRD outlines the comprehensive plan for refactoring TAIFA-FIALA from a funding tracker to an innovation archive. By creating a new repository with a redesigned architecture, we'll build a platform that serves as essential research infrastructure for documenting African AI excellence.

The success of this refactoring effort will be measured by our ability to transform subjects into co-researchers, align stakeholder interests around celebrating innovation, and pioneer next-generation systematic review methodology that could transform evidence synthesis across fields.

Through rigorous implementation of this plan, TAIFA-FIALA will become a valuable academic infrastructure that produces world-class datasets, enables participatory research, and facilitates evidence-based decision-making in the African AI ecosystem.