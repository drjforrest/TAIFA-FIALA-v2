"""
Advanced AI-Powered Deduplication Service for TAIFA-FIALA
Handles complex relationships like multiple innovations funded by one source
and linking related entities across different news events
"""

import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger
import openai

from config.settings import settings


class RelationshipType(Enum):
    """Types of relationships between news events"""
    SAME_EVENT = "same_event"  # Exact same event reported by different sources
    RELATED_FUNDING = "related_funding"  # Different companies funded by same program/investor
    RELATED_PARTNERSHIP = "related_partnership"  # Different aspects of same partnership
    SEQUENTIAL_FUNDING = "sequential_funding"  # Same company, different funding rounds
    PROGRAM_BENEFICIARIES = "program_beneficiaries"  # Multiple beneficiaries of same program
    ECOSYSTEM_RELATED = "ecosystem_related"  # Related companies in same ecosystem
    NONE = "none"


@dataclass
class EventRelationship:
    """Represents a relationship between two events"""
    source_event_id: str
    target_event_id: str
    relationship_type: RelationshipType
    confidence: float
    shared_entities: List[str]
    relationship_description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnhancedEventInfo:
    """Enhanced structured information about a news event with relationships"""
    event_id: str
    event_type: str  # funding, product_launch, partnership, acquisition, etc.
    primary_entity: str  # Main company/organization
    secondary_entities: List[str] = field(default_factory=list)  # Related companies, investors, partners
    funding_info: Dict[str, Any] = field(default_factory=dict)  # amount, round, investor, program
    product_info: Dict[str, Any] = field(default_factory=dict)  # name, category, features
    partnership_info: Dict[str, Any] = field(default_factory=dict)  # type, parties, scope
    event_date: Optional[datetime] = None
    location: Optional[str] = None
    description: str = ""
    key_phrases: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    relationships: List[EventRelationship] = field(default_factory=list)


@dataclass
class EventCluster:
    """A cluster of related events"""
    cluster_id: str
    cluster_type: str  # funding_program, partnership_network, company_journey, etc.
    primary_entity: str  # Main entity the cluster is about
    events: List[EnhancedEventInfo]
    canonical_event: EnhancedEventInfo
    relationship_summary: str
    total_impact: Dict[str, Any] = field(default_factory=dict)  # aggregated metrics


class AdvancedAIDeduplicationService:
    """Advanced AI-powered service for complex relationship analysis and deduplication"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.event_cache: Dict[str, EnhancedEventInfo] = {}
        self.relationship_cache: List[EventRelationship] = []
        
    async def analyze_complex_relationships(self, 
                                         articles: List[Dict[str, Any]]) -> Tuple[List[EventCluster], List[EnhancedEventInfo]]:
        """
        Analyze articles for complex relationships and create event clusters
        
        Returns:
            Tuple of (event_clusters, standalone_events)
        """
        
        logger.info(f"🔗 Starting advanced relationship analysis for {len(articles)} articles...")
        
        # Step 1: Extract enhanced event information from each article
        enhanced_events = []
        for i, article in enumerate(articles):
            try:
                event_info = await self._extract_enhanced_event_info(article, f"event_{i}")
                enhanced_events.append(event_info)
            except Exception as e:
                logger.error(f"❌ Error extracting enhanced event info: {e}")
                continue
        
        logger.info(f"📊 Extracted enhanced info for {len(enhanced_events)} events")
        
        # Step 2: Identify relationships between events
        relationships = await self._identify_event_relationships(enhanced_events)
        
        logger.info(f"🔗 Identified {len(relationships)} relationships")
        
        # Step 3: Create clusters based on relationships
        clusters, standalone_events = await self._create_event_clusters(enhanced_events, relationships)
        
        logger.info(f"📦 Created {len(clusters)} clusters with {len(standalone_events)} standalone events")
        
        return clusters, standalone_events

    async def _extract_enhanced_event_info(self, article: Dict[str, Any], event_id: str) -> EnhancedEventInfo:
        """Extract comprehensive event information with relationship potential"""
        
        prompt = f"""
        Analyze this African AI/tech news article and extract comprehensive structured information.
        Focus on identifying entities, funding details, partnerships, and relationship indicators.
        
        Article Title: {article.get('title', '')}
        Article Summary: {article.get('snippet', '')}
        Source: {article.get('source', '')}
        
        Extract the following information in JSON format:
        {{
            "event_type": "funding|product_launch|partnership|acquisition|research|award|program_launch|other",
            "primary_entity": "Main company/organization name",
            "secondary_entities": ["investor", "partner", "subsidiary", "etc"],
            "funding_info": {{
                "amount": "funding amount or null",
                "amount_usd": "amount in USD number or null", 
                "round": "seed|series_a|series_b|grant|other or null",
                "investor": "main investor name or null",
                "program": "funding program name or null",
                "is_part_of_larger_fund": "true/false if part of larger program"
            }},
            "product_info": {{
                "name": "product/service name or null",
                "category": "fintech|healthtech|agritech|edtech|other or null",
                "features": ["feature1", "feature2"] or []
            }},
            "partnership_info": {{
                "type": "strategic|technical|funding|distribution|other or null",
                "parties": ["party1", "party2"] or [],
                "scope": "partnership scope description or null"
            }},
            "location": "country/city mentioned or null",
            "key_phrases": ["important phrase 1", "phrase 2"],
            "relationship_indicators": {{
                "mentions_other_companies": ["company1", "company2"] or [],
                "mentions_funding_programs": ["program1", "program2"] or [],
                "mentions_ecosystem": ["ecosystem keyword1", "keyword2"] or []
            }},
            "description": "comprehensive event description",
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured information from African tech news. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            response_content = response.choices[0].message.content.strip()
            if not response_content:
                raise ValueError("Empty response from OpenAI")
            
            try:
                extracted_info = json.loads(response_content)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response: {response_content[:200]}...")
                raise e
            
            # Convert to EnhancedEventInfo object
            event = EnhancedEventInfo(
                event_id=event_id,
                event_type=extracted_info.get('event_type', 'other'),
                primary_entity=extracted_info.get('primary_entity', ''),
                secondary_entities=extracted_info.get('secondary_entities', []),
                funding_info=extracted_info.get('funding_info', {}),
                product_info=extracted_info.get('product_info', {}),
                partnership_info=extracted_info.get('partnership_info', {}),
                location=extracted_info.get('location'),
                description=extracted_info.get('description', ''),
                key_phrases=extracted_info.get('key_phrases', []),
                confidence_score=extracted_info.get('confidence', 0.5)
            )
            
            return event
            
        except Exception as e:
            logger.error(f"❌ Error extracting enhanced event information: {e}")
            # Return basic event info as fallback
            return EnhancedEventInfo(
                event_id=event_id,
                event_type='other',
                primary_entity=article.get('title', '')[:50],
                description=article.get('snippet', ''),
                confidence_score=0.3
            )

    async def _identify_event_relationships(self, events: List[EnhancedEventInfo]) -> List[EventRelationship]:
        """Identify relationships between events using AI analysis"""
        
        relationships = []
        
        # Compare each event with every other event
        for i, event1 in enumerate(events):
            for j, event2 in enumerate(events[i+1:], start=i+1):
                
                # Quick filtering to avoid unnecessary AI calls
                if not self._should_compare_events(event1, event2):
                    continue
                
                try:
                    relationship = await self._analyze_event_relationship(event1, event2)
                    if relationship and relationship.relationship_type != RelationshipType.NONE:
                        relationships.append(relationship)
                        
                        # Add reverse relationship if appropriate
                        if relationship.relationship_type in [RelationshipType.RELATED_FUNDING, 
                                                          RelationshipType.PROGRAM_BENEFICIARIES]:
                            reverse_relationship = EventRelationship(
                                source_event_id=event2.event_id,
                                target_event_id=event1.event_id,
                                relationship_type=relationship.relationship_type,
                                confidence=relationship.confidence,
                                shared_entities=relationship.shared_entities,
                                relationship_description=relationship.relationship_description
                            )
                            relationships.append(reverse_relationship)
                            
                except Exception as e:
                    logger.error(f"❌ Error analyzing relationship between {event1.event_id} and {event2.event_id}: {e}")
                    continue
        
        return relationships

    def _should_compare_events(self, event1: EnhancedEventInfo, event2: EnhancedEventInfo) -> bool:
        """Quick filter to determine if two events should be compared for relationships"""
        
        # Always compare if same primary entity
        if event1.primary_entity and event2.primary_entity and \
           event1.primary_entity.lower() == event2.primary_entity.lower():
            return True
        
        # Compare if share secondary entities
        if set(entity.lower() for entity in event1.secondary_entities) & set(entity.lower() for entity in event2.secondary_entities):
            return True
        
        # Compare funding events if they mention similar programs or investors
        if event1.event_type == 'funding' and event2.event_type == 'funding':
            investor1 = (event1.funding_info.get('investor') or '').lower()
            investor2 = (event2.funding_info.get('investor') or '').lower()
            program1 = (event1.funding_info.get('program') or '').lower()
            program2 = (event2.funding_info.get('program') or '').lower()
            
            if (investor1 and investor2 and investor1 == investor2) or \
               (program1 and program2 and program1 == program2):
                return True
        
        # Compare if same location and similar timeframe
        if event1.location and event2.location and event1.location.lower() == event2.location.lower():
            return True
        
        return False

    async def _analyze_event_relationship(self, event1: EnhancedEventInfo, event2: EnhancedEventInfo) -> Optional[EventRelationship]:
        """Use AI to analyze the relationship between two events"""
        
        prompt = f"""
        Analyze the relationship between these two African AI/tech news events.
        Determine if they are related and how.
        
        EVENT 1:
        Type: {event1.event_type}
        Primary Entity: {event1.primary_entity}
        Secondary Entities: {event1.secondary_entities}
        Funding Info: {event1.funding_info}
        Description: {event1.description}
        
        EVENT 2:
        Type: {event2.event_type}
        Primary Entity: {event2.primary_entity}
        Secondary Entities: {event2.secondary_entities}
        Funding Info: {event2.funding_info}
        Description: {event2.description}
        
        Analysis Focus:
        1. Are these the SAME event reported by different sources?
        2. Are these DIFFERENT companies funded by the same program/investor?
        3. Are these DIFFERENT funding rounds for the same company?
        4. Are these related to the same partnership or program?
        5. Are they part of the same ecosystem but unrelated events?
        
        Respond in JSON format:
        {{
            "relationship_type": "same_event|related_funding|sequential_funding|program_beneficiaries|related_partnership|ecosystem_related|none",
            "confidence": 0.0-1.0,
            "shared_entities": ["entity1", "entity2"],
            "relationship_description": "detailed explanation of the relationship",
            "supporting_evidence": ["evidence1", "evidence2"],
            "key_differences": ["difference1", "difference2"] or []
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at identifying relationships between African tech/AI news events. Be precise about relationship types."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            response_content = response.choices[0].message.content.strip()
            if not response_content:
                raise ValueError("Empty response from OpenAI")
            
            try:
                analysis = json.loads(response_content)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response: {response_content[:200]}...")
                raise e
            
            relationship_type_str = analysis.get('relationship_type', 'none')
            try:
                relationship_type = RelationshipType(relationship_type_str)
            except ValueError:
                relationship_type = RelationshipType.NONE
            
            if relationship_type == RelationshipType.NONE or analysis.get('confidence', 0) < 0.4:
                return None
            
            return EventRelationship(
                source_event_id=event1.event_id,
                target_event_id=event2.event_id,
                relationship_type=relationship_type,
                confidence=analysis.get('confidence', 0.5),
                shared_entities=analysis.get('shared_entities', []),
                relationship_description=analysis.get('relationship_description', ''),
                metadata={
                    'supporting_evidence': analysis.get('supporting_evidence', []),
                    'key_differences': analysis.get('key_differences', [])
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error in AI relationship analysis: {e}")
            return None

    async def _create_event_clusters(self, 
                                   events: List[EnhancedEventInfo], 
                                   relationships: List[EventRelationship]) -> Tuple[List[EventCluster], List[EnhancedEventInfo]]:
        """Create clusters of related events"""
        
        # Build relationship graph
        relationship_graph = {}
        for rel in relationships:
            if rel.source_event_id not in relationship_graph:
                relationship_graph[rel.source_event_id] = []
            relationship_graph[rel.source_event_id].append(rel)
        
        # Find connected components (clusters)
        visited = set()
        clusters = []
        standalone_events = []
        
        for event in events:
            if event.event_id in visited:
                continue
            
            # Find all events connected to this one
            cluster_events = []
            self._dfs_find_cluster(event.event_id, relationship_graph, visited, cluster_events, events)
            
            if len(cluster_events) > 1:
                # Create cluster
                cluster = await self._create_cluster_from_events(cluster_events, relationships)
                clusters.append(cluster)
            else:
                # Standalone event
                standalone_events.extend(cluster_events)
        
        return clusters, standalone_events

    def _dfs_find_cluster(self, 
                         event_id: str, 
                         relationship_graph: Dict[str, List[EventRelationship]], 
                         visited: Set[str], 
                         cluster_events: List[EnhancedEventInfo],
                         all_events: List[EnhancedEventInfo]):
        """DFS to find all events in a cluster"""
        
        if event_id in visited:
            return
        
        visited.add(event_id)
        
        # Find the event object
        event_obj = next((e for e in all_events if e.event_id == event_id), None)
        if event_obj:
            cluster_events.append(event_obj)
        
        # Visit connected events
        if event_id in relationship_graph:
            for relationship in relationship_graph[event_id]:
                self._dfs_find_cluster(relationship.target_event_id, relationship_graph, visited, cluster_events, all_events)

    async def _create_cluster_from_events(self, 
                                        events: List[EnhancedEventInfo], 
                                        all_relationships: List[EventRelationship]) -> EventCluster:
        """Create a cluster object from related events"""
        
        # Find relationships within this cluster
        event_ids = {e.event_id for e in events}
        cluster_relationships = [r for r in all_relationships 
                               if r.source_event_id in event_ids and r.target_event_id in event_ids]
        
        # Determine cluster type and primary entity
        cluster_type = await self._determine_cluster_type(events, cluster_relationships)
        primary_entity = await self._determine_primary_entity(events, cluster_relationships)
        
        # Select canonical event (best representative)
        canonical_event = self._select_canonical_event(events)
        
        # Generate relationship summary
        relationship_summary = await self._generate_relationship_summary(events, cluster_relationships)
        
        # Calculate total impact
        total_impact = self._calculate_cluster_impact(events)
        
        cluster = EventCluster(
            cluster_id=f"cluster_{canonical_event.event_id}",
            cluster_type=cluster_type,
            primary_entity=primary_entity,
            events=events,
            canonical_event=canonical_event,
            relationship_summary=relationship_summary,
            total_impact=total_impact
        )
        
        logger.info(f"📦 Created cluster: {cluster_type} for {primary_entity} with {len(events)} events")
        
        return cluster

    async def _determine_cluster_type(self, 
                                    events: List[EnhancedEventInfo], 
                                    relationships: List[EventRelationship]) -> str:
        """Determine the type of cluster based on events and relationships"""
        
        relationship_types = [r.relationship_type for r in relationships]
        
        # Funding program cluster (multiple companies funded by same source)
        if RelationshipType.RELATED_FUNDING in relationship_types or \
           RelationshipType.PROGRAM_BENEFICIARIES in relationship_types:
            return "funding_program"
        
        # Company journey cluster (same company, multiple events)
        if RelationshipType.SEQUENTIAL_FUNDING in relationship_types:
            return "company_journey"
        
        # Partnership network cluster
        if RelationshipType.RELATED_PARTNERSHIP in relationship_types:
            return "partnership_network"
        
        # Duplicate event cluster (same event, multiple sources)
        if RelationshipType.SAME_EVENT in relationship_types:
            return "duplicate_event"
        
        # Ecosystem cluster
        return "ecosystem_related"

    async def _determine_primary_entity(self, 
                                      events: List[EnhancedEventInfo], 
                                      relationships: List[EventRelationship]) -> str:
        """Determine the primary entity for the cluster"""
        
        # Count entity mentions
        entity_counts = {}
        
        for event in events:
            # Count primary entity
            if event.primary_entity:
                primary = event.primary_entity.lower()
                entity_counts[primary] = entity_counts.get(primary, 0) + 2  # Higher weight for primary
            
            # Count secondary entities
            for secondary in event.secondary_entities:
                sec = secondary.lower()
                entity_counts[sec] = entity_counts.get(sec, 0) + 1
        
        # Return most mentioned entity
        if entity_counts:
            return max(entity_counts, key=entity_counts.get).title()
        
        return events[0].primary_entity if events else "Unknown"

    def _select_canonical_event(self, events: List[EnhancedEventInfo]) -> EnhancedEventInfo:
        """Select the best event to represent the cluster"""
        
        # Score events based on multiple factors
        scored_events = []
        
        for event in events:
            score = 0
            
            # Confidence score
            score += event.confidence_score * 20
            
            # Description completeness
            score += min(len(event.description) / 50, 10)
            
            # Number of entities (indicates comprehensiveness)
            score += len(event.secondary_entities) * 2
            
            # Funding events get priority if they have amount info
            if event.event_type == 'funding' and event.funding_info.get('amount'):
                score += 15
            
            # Events with location info get bonus
            if event.location:
                score += 5
            
            scored_events.append((event, score))
        
        # Return highest scoring event
        return max(scored_events, key=lambda x: x[1])[0]

    async def _generate_relationship_summary(self, 
                                           events: List[EnhancedEventInfo], 
                                           relationships: List[EventRelationship]) -> str:
        """Generate a summary of relationships in the cluster"""
        
        if not relationships:
            return f"Cluster of {len(events)} related events"
        
        relationship_types = [r.relationship_type.value for r in relationships]
        most_common_relationship = max(set(relationship_types), key=relationship_types.count)
        
        summaries = {
            'related_funding': f"Multiple companies funded by the same source: {len(events)} funding events",
            'sequential_funding': f"Company funding journey: {len(events)} funding rounds",
            'program_beneficiaries': f"Program beneficiaries: {len(events)} companies in same program",
            'same_event': f"Same event reported by {len(events)} different sources",
            'related_partnership': f"Partnership network involving {len(events)} related announcements",
            'ecosystem_related': f"Ecosystem cluster: {len(events)} related events"
        }
        
        return summaries.get(most_common_relationship, f"Related events cluster: {len(events)} events")

    def _calculate_cluster_impact(self, events: List[EnhancedEventInfo]) -> Dict[str, Any]:
        """Calculate aggregated impact metrics for the cluster"""
        
        impact = {
            'total_events': len(events),
            'event_types': {},
            'funding_total': 0,
            'companies_involved': set(),
            'locations': set(),
            'sectors': set()
        }
        
        for event in events:
            # Count event types
            event_type = event.event_type
            impact['event_types'][event_type] = impact['event_types'].get(event_type, 0) + 1
            
            # Sum funding amounts
            if event.funding_info.get('amount_usd'):
                try:
                    amount = float(event.funding_info['amount_usd'])
                    impact['funding_total'] += amount
                except:
                    pass
            
            # Collect entities
            if event.primary_entity:
                impact['companies_involved'].add(event.primary_entity)
            impact['companies_involved'].update(event.secondary_entities)
            
            # Collect locations
            if event.location:
                impact['locations'].add(event.location)
            
            # Collect sectors
            if event.product_info.get('category'):
                impact['sectors'].add(event.product_info['category'])
        
        # Convert sets to lists for JSON serialization
        impact['companies_involved'] = list(impact['companies_involved'])
        impact['locations'] = list(impact['locations'])
        impact['sectors'] = list(impact['sectors'])
        
        return impact


# Global advanced AI deduplication service instance
advanced_ai_dedup_service = AdvancedAIDeduplicationService()


# Main function for use in ETL pipeline
async def analyze_articles_with_complex_relationships(articles: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Analyze articles for complex relationships and return deduplicated results with relationship info
    
    Returns:
        Tuple of (canonical_articles, relationship_metadata)
    """
    
    clusters, standalone_events = await advanced_ai_dedup_service.analyze_complex_relationships(articles)
    
    canonical_articles = []
    relationship_metadata = {
        'clusters': [],
        'standalone_events': len(standalone_events),
        'total_relationships': 0
    }
    
    # Process clusters
    for cluster in clusters:
        # Convert canonical event back to article format
        canonical_article = None
        for article in articles:
            # Find original article that matches canonical event
            if cluster.canonical_event.primary_entity.lower() in article.get('title', '').lower() or \
               cluster.canonical_event.primary_entity.lower() in article.get('snippet', '').lower():
                canonical_article = article.copy()
                break
        
        if canonical_article:
            # Add cluster metadata
            canonical_article['cluster_info'] = {
                'cluster_id': cluster.cluster_id,
                'cluster_type': cluster.cluster_type,
                'cluster_size': len(cluster.events),
                'primary_entity': cluster.primary_entity,
                'relationship_summary': cluster.relationship_summary,
                'total_impact': cluster.total_impact,
                'related_articles': len(cluster.events) - 1
            }
            canonical_articles.append(canonical_article)
            
            # Add to metadata
            relationship_metadata['clusters'].append({
                'cluster_id': cluster.cluster_id,
                'type': cluster.cluster_type,
                'primary_entity': cluster.primary_entity,
                'event_count': len(cluster.events),
                'summary': cluster.relationship_summary
            })
    
    # Add standalone events
    for event in standalone_events:
        # Find original article
        for article in articles:
            if event.primary_entity.lower() in article.get('title', '').lower() or \
               event.primary_entity.lower() in article.get('snippet', '').lower():
                canonical_articles.append(article)
                break
    
    # Count total relationships
    relationship_metadata['total_relationships'] = sum(len(cluster.events) - 1 for cluster in clusters)
    
    logger.info(f"🎯 Advanced deduplication complete: {len(canonical_articles)} canonical articles, {len(clusters)} clusters")
    
    return canonical_articles, relationship_metadata
