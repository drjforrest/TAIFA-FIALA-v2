"""
Citation & Reference Analysis Service for TAIFA-FIALA
Implements Phase 1 of the Citations Expansion Strategy:
- Citation network analysis
- Reference mining and extraction
- Impact scoring
- Knowledge flow mapping from academia to industry

Focus on maximizing intelligence from existing data for competitive advantage.
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
import json

from loguru import logger
from config.database import get_supabase
from services.vector_service import get_vector_service


@dataclass
class CitationRelation:
    """Represents a citation relationship between publications"""
    citing_paper_id: str
    cited_paper_id: str
    citation_context: str
    confidence_score: float
    extracted_at: datetime


@dataclass 
class ImpactMetrics:
    """Impact metrics for a publication or innovation"""
    citation_count: int
    h_index_contribution: float
    downstream_innovations: int
    academic_to_industry_flow: float
    influence_score: float
    network_centrality: float


@dataclass
class KnowledgeFlowPath:
    """Tracks knowledge flow from research to innovation"""
    source_publication_id: str
    target_innovation_id: str
    flow_strength: float
    intermediate_nodes: List[str]
    time_to_market: Optional[int]  # days
    transformation_type: str  # "direct", "evolved", "combined"


class CitationsAnalysisService:
    """Advanced citation and reference analysis for competitive intelligence"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.vector_service = None
        
        # Citation extraction patterns
        self.citation_patterns = [
            r'\[(\d+)\]',  # [1], [2], etc.
            r'\(([^)]+\d{4}[^)]*)\)',  # (Author, 2023)
            r'doi:(\S+)',  # DOI references
            r'arxiv:(\d+\.\d+)',  # ArXiv references
            r'PMID:?\s*(\d+)',  # PubMed IDs
        ]
        
        # African institution patterns for knowledge flow
        self.african_institution_patterns = [
            r'University of (\w+)',
            r'(\w+) Institute of Technology',
            r'Council for Scientific and Industrial Research',
            r'African (\w+) Centre',
        ]
    
    async def initialize(self):
        """Initialize services"""
        try:
            self.vector_service = await get_vector_service()
            logger.info("Citations analysis service initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize citations service: {e}")
            return False
    
    # CITATION NETWORK ANALYSIS
    async def extract_citations_from_publications(self, batch_size: int = 50) -> List[CitationRelation]:
        """Extract citation relationships from publication content"""
        try:
            # Get publications with abstracts and full text
            response = self.supabase.table('publications').select(
                'id, title, abstract, content, doi, arxiv_id, pubmed_id, publication_date'
            ).limit(1000).execute()
            
            if not response.data:
                return []
            
            citations = []
            
            for pub in response.data:
                pub_citations = await self._extract_citations_from_text(
                    pub['id'],
                    pub.get('abstract', '') + ' ' + pub.get('content', ''),
                    pub.get('title', '')
                )
                citations.extend(pub_citations)
            
            # Store citation relationships
            await self._store_citation_relationships(citations)
            
            logger.info(f"Extracted {len(citations)} citation relationships")
            return citations
            
        except Exception as e:
            logger.error(f"Error extracting citations: {e}")
            return []
    
    async def _extract_citations_from_text(self, paper_id: str, text: str, title: str) -> List[CitationRelation]:
        """Extract citations from paper text using multiple patterns"""
        citations = []
        
        if not text:
            return citations
        
        # Extract references section
        ref_section = self._extract_references_section(text)
        
        # Pattern matching for different citation formats
        for pattern in self.citation_patterns:
            matches = re.finditer(pattern, ref_section, re.IGNORECASE)
            for match in matches:
                citation = await self._resolve_citation_reference(
                    paper_id, match.group(), match.group(0), text
                )
                if citation:
                    citations.append(citation)
        
        return citations
    
    def _extract_references_section(self, text: str) -> str:
        """Extract the references section from paper text"""
        # Look for references section markers
        ref_markers = [
            r'References?\s*\n',
            r'Bibliography\s*\n',
            r'Works\s+Cited\s*\n',
            r'\nReferences?\s*$'
        ]
        
        for marker in ref_markers:
            match = re.search(marker, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return text[match.start():]
        
        return text  # Return full text if no references section found
    
    async def _resolve_citation_reference(self, citing_id: str, ref_text: str, 
                                        context: str, full_text: str) -> Optional[CitationRelation]:
        """Resolve citation reference to actual publication"""
        try:
            # Try to match with DOI
            doi_match = re.search(r'doi:(\S+)', ref_text, re.IGNORECASE)
            if doi_match:
                doi = doi_match.group(1)
                response = self.supabase.table('publications').select('id').eq('doi', doi).execute()
                if response.data:
                    return CitationRelation(
                        citing_paper_id=citing_id,
                        cited_paper_id=response.data[0]['id'],
                        citation_context=context[:200],
                        confidence_score=0.95,
                        extracted_at=datetime.now()
                    )
            
            # Try to match with ArXiv ID
            arxiv_match = re.search(r'arxiv:(\d+\.\d+)', ref_text, re.IGNORECASE)
            if arxiv_match:
                arxiv_id = arxiv_match.group(1)
                response = self.supabase.table('publications').select('id').eq('arxiv_id', arxiv_id).execute()
                if response.data:
                    return CitationRelation(
                        citing_paper_id=citing_id,
                        cited_paper_id=response.data[0]['id'],
                        citation_context=context[:200],
                        confidence_score=0.9,
                        extracted_at=datetime.now()
                    )
            
            # Try fuzzy title matching using vector search
            if self.vector_service:
                similar_papers = await self.vector_service.search_publications(
                    query=ref_text[:100],
                    top_k=3
                )
                
                for paper in similar_papers:
                    if paper.score > 0.85:  # High similarity threshold
                        return CitationRelation(
                            citing_paper_id=citing_id,
                            cited_paper_id=paper.metadata.get('publication_id'),
                            citation_context=context[:200],
                            confidence_score=paper.score * 0.7,  # Reduce confidence for fuzzy match
                            extracted_at=datetime.now()
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Error resolving citation: {e}")
            return None
    
    async def _store_citation_relationships(self, citations: List[CitationRelation]):
        """Store citation relationships in database"""
        try:
            citation_data = []
            for citation in citations:
                citation_data.append({
                    'citing_paper_id': citation.citing_paper_id,
                    'cited_paper_id': citation.cited_paper_id,
                    'citation_context': citation.citation_context,
                    'confidence_score': citation.confidence_score,
                    'extracted_at': citation.extracted_at.isoformat()
                })
            
            if citation_data:
                response = self.supabase.table('citation_relationships').insert(citation_data).execute()
                logger.info(f"Stored {len(citation_data)} citation relationships")
                
        except Exception as e:
            logger.error(f"Error storing citations: {e}")
    
    # IMPACT SCORING
    async def calculate_publication_impact_scores(self) -> Dict[str, ImpactMetrics]:
        """Calculate comprehensive impact metrics for all publications"""
        try:
            # Get all publications with citation data
            pubs_response = self.supabase.table('publications').select('id, title, publication_date').execute()
            citations_response = self.supabase.table('citation_relationships').select('*').execute()
            
            if not pubs_response.data:
                return {}
            
            publications = {pub['id']: pub for pub in pubs_response.data}
            citations = citations_response.data if citations_response.data else []
            
            # Build citation network
            citation_graph = defaultdict(list)
            citation_counts = defaultdict(int)
            
            for citation in citations:
                citing_id = citation['citing_paper_id']
                cited_id = citation['cited_paper_id']
                citation_graph[cited_id].append(citing_id)
                citation_counts[cited_id] += 1
            
            impact_metrics = {}
            
            for pub_id, pub in publications.items():
                metrics = await self._calculate_individual_impact(
                    pub_id, pub, citation_graph, citation_counts
                )
                impact_metrics[pub_id] = metrics
            
            # Store impact metrics
            await self._store_impact_metrics(impact_metrics)
            
            return impact_metrics
            
        except Exception as e:
            logger.error(f"Error calculating impact scores: {e}")
            return {}
    
    async def _calculate_individual_impact(self, pub_id: str, pub: Dict, 
                                         citation_graph: Dict, citation_counts: Dict) -> ImpactMetrics:
        """Calculate impact metrics for individual publication"""
        try:
            citation_count = citation_counts.get(pub_id, 0)
            
            # Calculate h-index contribution (simplified)
            citing_papers = citation_graph.get(pub_id, [])
            h_contribution = min(citation_count, len(citing_papers))
            
            # Check for downstream innovations (papers that became products)
            downstream_innovations = await self._count_downstream_innovations(pub_id)
            
            # Calculate academic-to-industry flow
            industry_flow = await self._calculate_industry_flow_score(pub_id, citing_papers)
            
            # Network centrality (simplified PageRank-like score)
            centrality = self._calculate_network_centrality(pub_id, citation_graph)
            
            # Overall influence score
            influence = self._calculate_influence_score(
                citation_count, h_contribution, downstream_innovations, 
                industry_flow, centrality
            )
            
            return ImpactMetrics(
                citation_count=citation_count,
                h_index_contribution=h_contribution,
                downstream_innovations=downstream_innovations,
                academic_to_industry_flow=industry_flow,
                influence_score=influence,
                network_centrality=centrality
            )
            
        except Exception as e:
            logger.error(f"Error calculating individual impact for {pub_id}: {e}")
            return ImpactMetrics(0, 0, 0, 0, 0, 0)
    
    async def _count_downstream_innovations(self, pub_id: str) -> int:
        """Count innovations that reference this publication"""
        try:
            # Check if any innovations reference this publication
            response = self.supabase.table('innovations').select('id, publications').execute()
            
            if not response.data:
                return 0
            
            count = 0
            for innovation in response.data:
                publications = innovation.get('publications', [])
                if any(pub.get('publication_id') == pub_id for pub in publications):
                    count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Error counting downstream innovations: {e}")
            return 0
    
    async def _calculate_industry_flow_score(self, pub_id: str, citing_papers: List[str]) -> float:
        """Calculate academic-to-industry knowledge flow score"""
        if not citing_papers:
            return 0.0
        
        try:
            industry_citations = 0
            
            for citing_id in citing_papers:
                # Get citing paper details
                response = self.supabase.table('publications').select(
                    'authors, abstract, content'
                ).eq('id', citing_id).execute()
                
                if response.data:
                    paper = response.data[0]
                    
                    # Check for industry affiliation indicators
                    text = (paper.get('abstract', '') + ' ' + 
                           ' '.join(paper.get('authors', []))).lower()
                    
                    industry_indicators = [
                        'ltd', 'inc', 'corp', 'company', 'startup', 
                        'commercial', 'product', 'deployment', 'market'
                    ]
                    
                    if any(indicator in text for indicator in industry_indicators):
                        industry_citations += 1
            
            return industry_citations / len(citing_papers)
            
        except Exception as e:
            logger.error(f"Error calculating industry flow: {e}")
            return 0.0
    
    def _calculate_network_centrality(self, pub_id: str, citation_graph: Dict) -> float:
        """Calculate network centrality score (simplified PageRank)"""
        try:
            # Simple centrality based on citation connections
            direct_citations = len(citation_graph.get(pub_id, []))
            
            # Weight by citing papers' own citation counts
            weighted_centrality = 0
            for citing_id in citation_graph.get(pub_id, []):
                citing_citations = len(citation_graph.get(citing_id, []))
                weighted_centrality += 1 + (citing_citations * 0.1)
            
            return min(weighted_centrality, 10.0)  # Cap at 10.0
            
        except Exception as e:
            logger.error(f"Error calculating centrality: {e}")
            return 0.0
    
    def _calculate_influence_score(self, citations: int, h_contrib: float, 
                                 downstream: int, industry_flow: float, 
                                 centrality: float) -> float:
        """Calculate overall influence score"""
        # Weighted combination of different factors
        weights = {
            'citations': 0.3,
            'h_index': 0.2,
            'downstream': 0.25,
            'industry': 0.15,
            'centrality': 0.1
        }
        
        normalized_scores = {
            'citations': min(citations / 50.0, 1.0),  # Normalize to max 50 citations
            'h_index': min(h_contrib / 20.0, 1.0),   # Normalize to max h=20
            'downstream': min(downstream / 10.0, 1.0), # Normalize to max 10 innovations
            'industry': industry_flow,  # Already 0-1
            'centrality': centrality / 10.0  # Normalize centrality
        }
        
        influence = sum(weights[key] * normalized_scores[key] for key in weights)
        return round(influence * 100, 2)  # Return as percentage
    
    async def _store_impact_metrics(self, impact_metrics: Dict[str, ImpactMetrics]):
        """Store impact metrics in database"""
        try:
            metrics_data = []
            for pub_id, metrics in impact_metrics.items():
                metrics_data.append({
                    'publication_id': pub_id,
                    'citation_count': metrics.citation_count,
                    'h_index_contribution': metrics.h_index_contribution,
                    'downstream_innovations': metrics.downstream_innovations,
                    'academic_to_industry_flow': metrics.academic_to_industry_flow,
                    'influence_score': metrics.influence_score,
                    'network_centrality': metrics.network_centrality,
                    'calculated_at': datetime.now().isoformat()
                })
            
            if metrics_data:
                # Update publications table with impact metrics
                for data in metrics_data:
                    pub_id = data.pop('publication_id')
                    self.supabase.table('publications').update({
                        'impact_metrics': data
                    }).eq('id', pub_id).execute()
                
                logger.info(f"Stored impact metrics for {len(metrics_data)} publications")
                
        except Exception as e:
            logger.error(f"Error storing impact metrics: {e}")
    
    # KNOWLEDGE FLOW MAPPING
    async def map_research_to_innovation_flows(self) -> List[KnowledgeFlowPath]:
        """Map knowledge flows from research papers to innovations"""
        try:
            # Get all publications and innovations
            pubs_response = self.supabase.table('publications').select(
                'id, title, abstract, publication_date, keywords'
            ).execute()
            
            innovations_response = self.supabase.table('innovations').select(
                'id, title, description, creation_date, publications, tags'
            ).execute()
            
            if not pubs_response.data or not innovations_response.data:
                return []
            
            publications = pubs_response.data
            innovations = innovations_response.data
            
            flow_paths = []
            
            for innovation in innovations:
                innovation_flows = await self._identify_knowledge_sources(
                    innovation, publications
                )
                flow_paths.extend(innovation_flows)
            
            # Store knowledge flow data
            await self._store_knowledge_flows(flow_paths)
            
            return flow_paths
            
        except Exception as e:
            logger.error(f"Error mapping knowledge flows: {e}")
            return []
    
    async def _identify_knowledge_sources(self, innovation: Dict, 
                                        publications: List[Dict]) -> List[KnowledgeFlowPath]:
        """Identify research sources that contributed to an innovation"""
        flows = []
        
        try:
            innovation_text = innovation.get('title', '') + ' ' + innovation.get('description', '')
            innovation_date = innovation.get('creation_date')
            
            if not innovation_date:
                return flows
            
            innovation_date = datetime.fromisoformat(innovation_date.replace('Z', '+00:00'))
            
            # Use vector similarity to find related publications
            if self.vector_service:
                similar_pubs = await self.vector_service.search_publications(
                    query=innovation_text,
                    top_k=10
                )
                
                for pub_result in similar_pubs:
                    if pub_result.score > 0.7:  # High similarity threshold
                        pub_id = pub_result.metadata.get('publication_id')
                        
                        # Find the publication details
                        pub = next((p for p in publications if p['id'] == pub_id), None)
                        if not pub:
                            continue
                        
                        pub_date = pub.get('publication_date')
                        if not pub_date:
                            continue
                        
                        pub_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                        
                        # Only consider papers published before the innovation
                        if pub_date < innovation_date:
                            time_to_market = (innovation_date - pub_date).days
                            
                            flow = KnowledgeFlowPath(
                                source_publication_id=pub_id,
                                target_innovation_id=innovation['id'],
                                flow_strength=pub_result.score,
                                intermediate_nodes=[],  # Could be enhanced with citation chains
                                time_to_market=time_to_market,
                                transformation_type=self._classify_transformation_type(
                                    pub_result.score, time_to_market
                                )
                            )
                            flows.append(flow)
            
            return flows
            
        except Exception as e:
            logger.error(f"Error identifying knowledge sources: {e}")
            return []
    
    def _classify_transformation_type(self, similarity: float, time_to_market: int) -> str:
        """Classify the type of knowledge transformation"""
        if similarity > 0.9 and time_to_market < 365:
            return "direct"
        elif similarity > 0.8 and time_to_market < 730:
            return "evolved"
        else:
            return "combined"
    
    async def _store_knowledge_flows(self, flows: List[KnowledgeFlowPath]):
        """Store knowledge flow paths in database"""
        try:
            flow_data = []
            for flow in flows:
                flow_data.append({
                    'source_publication_id': flow.source_publication_id,
                    'target_innovation_id': flow.target_innovation_id,
                    'flow_strength': flow.flow_strength,
                    'intermediate_nodes': flow.intermediate_nodes,
                    'time_to_market_days': flow.time_to_market,
                    'transformation_type': flow.transformation_type,
                    'mapped_at': datetime.now().isoformat()
                })
            
            if flow_data:
                response = self.supabase.table('knowledge_flows').insert(flow_data).execute()
                logger.info(f"Stored {len(flow_data)} knowledge flow paths")
                
        except Exception as e:
            logger.error(f"Error storing knowledge flows: {e}")
    
    # ANALYTICS AND REPORTING
    async def generate_citation_network_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive citation network analytics"""
        try:
            # Get citation relationships
            citations_response = self.supabase.table('citation_relationships').select('*').execute()
            citations = citations_response.data if citations_response.data else []
            
            # Get publications with impact metrics
            pubs_response = self.supabase.table('publications').select(
                'id, title, impact_metrics, publication_date, authors'
            ).execute()
            publications = pubs_response.data if pubs_response.data else []
            
            # Network analysis
            total_citations = len(citations)
            total_publications = len(publications)
            
            # Most influential papers
            influential_papers = sorted(
                [p for p in publications if p.get('impact_metrics')],
                key=lambda x: x['impact_metrics'].get('influence_score', 0),
                reverse=True
            )[:10]
            
            # Citation patterns over time
            citation_timeline = self._analyze_citation_timeline(citations, publications)
            
            # Network density and connectivity
            network_stats = self._calculate_network_statistics(citations, publications)
            
            # Knowledge flow patterns
            flow_response = self.supabase.table('knowledge_flows').select('*').execute()
            flows = flow_response.data if flow_response.data else []
            
            flow_analytics = self._analyze_knowledge_flows(flows)
            
            return {
                'network_overview': {
                    'total_publications': total_publications,
                    'total_citations': total_citations,
                    'citation_density': total_citations / max(total_publications, 1),
                    'average_citations_per_paper': total_citations / max(total_publications, 1)
                },
                'influential_research': [
                    {
                        'id': paper['id'],
                        'title': paper['title'],
                        'influence_score': paper['impact_metrics'].get('influence_score', 0),
                        'citation_count': paper['impact_metrics'].get('citation_count', 0)
                    }
                    for paper in influential_papers
                ],
                'citation_timeline': citation_timeline,
                'network_statistics': network_stats,
                'knowledge_flow_analytics': flow_analytics,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating citation analytics: {e}")
            return {}
    
    def _analyze_citation_timeline(self, citations: List[Dict], publications: List[Dict]) -> List[Dict]:
        """Analyze citation patterns over time"""
        try:
            pub_dates = {pub['id']: pub.get('publication_date') for pub in publications if pub.get('publication_date')}
            
            timeline = defaultdict(int)
            
            for citation in citations:
                cited_id = citation['cited_paper_id']
                if cited_id in pub_dates:
                    pub_date = pub_dates[cited_id]
                    try:
                        date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                        month_key = date.strftime('%Y-%m')
                        timeline[month_key] += 1
                    except:
                        continue
            
            return [
                {'month': month, 'citations': count}
                for month, count in sorted(timeline.items())
            ]
            
        except Exception as e:
            logger.error(f"Error analyzing citation timeline: {e}")
            return []
    
    def _calculate_network_statistics(self, citations: List[Dict], publications: List[Dict]) -> Dict:
        """Calculate network connectivity statistics"""
        try:
            pub_ids = set(pub['id'] for pub in publications)
            
            # Build adjacency lists
            citation_graph = defaultdict(set)
            reverse_graph = defaultdict(set)
            
            for citation in citations:
                citing = citation['citing_paper_id']
                cited = citation['cited_paper_id']
                
                if citing in pub_ids and cited in pub_ids:
                    citation_graph[citing].add(cited)
                    reverse_graph[cited].add(citing)
            
            # Calculate statistics
            connected_papers = len([p for p in pub_ids if p in citation_graph or p in reverse_graph])
            isolation_rate = (len(pub_ids) - connected_papers) / max(len(pub_ids), 1)
            
            # Average degree (citations per paper)
            avg_out_degree = sum(len(refs) for refs in citation_graph.values()) / max(len(pub_ids), 1)
            avg_in_degree = sum(len(cites) for cites in reverse_graph.values()) / max(len(pub_ids), 1)
            
            return {
                'connected_papers': connected_papers,
                'isolated_papers': len(pub_ids) - connected_papers,
                'isolation_rate': round(isolation_rate * 100, 2),
                'average_references_per_paper': round(avg_out_degree, 2),
                'average_citations_per_paper': round(avg_in_degree, 2),
                'network_connectivity': round((1 - isolation_rate) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating network statistics: {e}")
            return {}
    
    def _analyze_knowledge_flows(self, flows: List[Dict]) -> Dict:
        """Analyze knowledge flow patterns"""
        try:
            if not flows:
                return {'total_flows': 0}
            
            # Time to market analysis
            time_to_market = [f['time_to_market_days'] for f in flows if f.get('time_to_market_days')]
            avg_time_to_market = sum(time_to_market) / len(time_to_market) if time_to_market else 0
            
            # Transformation type distribution
            transformation_types = Counter(f['transformation_type'] for f in flows)
            
            # Flow strength distribution
            flow_strengths = [f['flow_strength'] for f in flows if f.get('flow_strength')]
            avg_flow_strength = sum(flow_strengths) / len(flow_strengths) if flow_strengths else 0
            
            return {
                'total_flows': len(flows),
                'average_time_to_market_days': round(avg_time_to_market, 1),
                'transformation_types': dict(transformation_types),
                'average_flow_strength': round(avg_flow_strength, 3),
                'research_to_innovation_rate': len(flows)  # Could be normalized by total publications
            }
            
        except Exception as e:
            logger.error(f"Error analyzing knowledge flows: {e}")
            return {}


# Global service instance
citations_service = CitationsAnalysisService()