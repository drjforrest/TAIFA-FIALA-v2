"""
Comprehensive Tests for AI Backfill Service
===========================================

Test suite for the Perplexity + OpenAI backfilling system.
Tests both unit functionality and integration scenarios.
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from services.ai_backfill_service import (
    AIBackfillService, 
    BackfillJob, 
    BackfillStatus, 
    BackfillPriority,
    MissingField,
    BackfillResult
)


class TestAIBackfillService:
    """Test suite for AIBackfillService"""
    
    @pytest.fixture
    def mock_innovation(self):
        """Mock innovation data for testing"""
        return {
            'id': 'test-innovation-123',
            'title': 'Flutterwave',
            'description': 'Nigerian fintech company providing payment infrastructure for Africa',
            'innovation_type': 'FinTech',
            'verification_status': 'verified',
            'fundings': [],  # Missing funding info
            'website_url': None,  # Missing website
            'organizations': [],  # Missing organization info
            'individuals': [],  # Missing team info
            'impact_metrics': {},  # Missing metrics
            'github_url': None,
            'demo_url': None
        }
    
    @pytest.fixture
    def backfill_service(self):
        """Create AIBackfillService instance with mocked APIs"""
        service = AIBackfillService()
        service.openai_client = AsyncMock()
        service.perplexity_key = 'test-perplexity-key'
        service.serper_key = 'test-serper-key'
        return service
    
    @pytest.mark.asyncio
    async def test_analyze_missing_fields(self, backfill_service, mock_innovation):
        """Test identification of missing fields"""
        
        missing_fields = await backfill_service.analyze_missing_fields(mock_innovation)
        
        # Should identify all missing critical and high-priority fields
        field_names = [field.field_name for field in missing_fields]
        assert 'funding_amount' in field_names
        assert 'website_url' in field_names
        assert 'founding_organization' in field_names
        assert 'key_team_members' in field_names
        
        # Check priorities are assigned correctly
        funding_field = next(f for f in missing_fields if f.field_name == 'funding_amount')
        assert funding_field.priority == BackfillPriority.CRITICAL
        
        website_field = next(f for f in missing_fields if f.field_name == 'website_url')
        assert website_field.priority == BackfillPriority.CRITICAL
    
    @pytest.mark.asyncio
    async def test_create_backfill_job(self, backfill_service, mock_innovation):
        """Test backfill job creation"""
        
        job = await backfill_service.create_backfill_job(mock_innovation)
        
        assert job is not None
        assert job.innovation_id == 'test-innovation-123'
        assert job.innovation_title == 'Flutterwave'
        assert job.status == BackfillStatus.PENDING
        assert len(job.missing_fields) > 0
        assert job.priority == BackfillPriority.CRITICAL  # Should have critical priority due to missing funding
    
    @pytest.mark.asyncio
    async def test_create_perplexity_prompt(self, backfill_service):
        """Test Perplexity prompt creation for different field types"""
        
        job = BackfillJob(
            job_id='test-job',
            innovation_id='test-123',
            innovation_title='Test Innovation',
            innovation_description='A test AI innovation',
            missing_fields=[],
            status=BackfillStatus.PENDING,
            priority=BackfillPriority.HIGH,
            created_at=datetime.now()
        )
        
        funding_field = MissingField(
            field_name='funding_amount',
            field_type='funding',
            priority=BackfillPriority.CRITICAL,
            search_strategy='perplexity',
            estimated_cost=0.10
        )
        
        prompt = backfill_service._create_perplexity_prompt(job, funding_field)
        
        assert 'Test Innovation' in prompt
        assert 'funding' in prompt.lower()
        assert 'investment rounds' in prompt.lower()
        assert 'investor names' in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_parse_with_openai_funding(self, backfill_service):
        """Test OpenAI parsing of Perplexity output for funding"""
        
        mock_perplexity_content = """
        Flutterwave has raised $250 million in Series C funding led by Avenir Growth Capital.
        The funding round was completed in February 2022 and values the company at $3 billion.
        Other investors include Tiger Global and Green Visor Capital.
        """
        
        funding_field = MissingField(
            field_name='funding_amount',
            field_type='funding',
            priority=BackfillPriority.CRITICAL,
            search_strategy='perplexity',
            estimated_cost=0.10
        )
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "value": {
                "amount": 250000000,
                "currency": "USD",
                "round": "Series C",
                "investor": "Avenir Growth Capital"
            },
            "confidence": 0.9,
            "supporting_evidence": ["$250 million in Series C funding", "led by Avenir Growth Capital"],
            "source_reliability": "high",
            "verification_notes": "Multiple sources confirm the funding amount"
        })
        
        backfill_service.openai_client.chat.completions.create.return_value = mock_response
        
        result = await backfill_service._parse_with_openai(mock_perplexity_content, funding_field)
        
        assert result is not None
        assert result['confidence'] == 0.9
        assert result['value']['amount'] == 250000000
        assert result['value']['currency'] == 'USD'
        assert result['value']['round'] == 'Series C'
    
    @pytest.mark.asyncio
    async def test_daily_cost_reset(self, backfill_service):
        """Test daily cost tracking and reset"""
        
        # Set yesterday as last reset
        backfill_service.last_cost_reset = datetime.now().date() - timedelta(days=1)
        backfill_service.current_daily_cost = 25.0
        
        # Check reset triggers
        backfill_service._check_daily_cost_reset()
        
        assert backfill_service.current_daily_cost == 0.0
        assert backfill_service.last_cost_reset == datetime.now().date()
    
    @pytest.mark.asyncio
    async def test_budget_limiting(self, backfill_service, mock_innovation):
        """Test that daily budget limits are respected"""
        
        # Set high daily cost to trigger budget limit
        backfill_service.current_daily_cost = 49.0  # Close to $50 limit
        backfill_service.daily_cost_limit = 50.0
        
        job = await backfill_service.create_backfill_job(mock_innovation)
        processed_job = await backfill_service.process_backfill_job(job)
        
        # Should be skipped due to budget
        assert processed_job.status == BackfillStatus.SKIPPED
        assert 'cost limit' in processed_job.error_message.lower()
    
    @pytest.mark.asyncio
    @patch('services.ai_backfill_service.PerplexityAfricanAIModule')
    async def test_backfill_with_perplexity_integration(self, mock_perplexity_class, backfill_service):
        """Test integration with Perplexity API"""
        
        # Mock Perplexity module
        mock_perplexity = AsyncMock()
        mock_perplexity._call_perplexity_api.return_value = {
            'choices': [{
                'message': {
                    'content': 'Flutterwave raised $250 million in Series C funding from Avenir Growth Capital.'
                }
            }]
        }
        
        mock_perplexity_class.return_value.__aenter__.return_value = mock_perplexity
        
        # Mock OpenAI parsing
        mock_openai_response = MagicMock()
        mock_openai_response.choices[0].message.content = json.dumps({
            "value": {"amount": 250000000, "currency": "USD"},
            "confidence": 0.85
        })
        backfill_service.openai_client.chat.completions.create.return_value = mock_openai_response
        
        job = BackfillJob(
            job_id='test-job',
            innovation_id='test-123',
            innovation_title='Flutterwave',
            innovation_description='Fintech company',
            missing_fields=[],
            status=BackfillStatus.PENDING,
            priority=BackfillPriority.HIGH,
            created_at=datetime.now()
        )
        
        funding_field = MissingField(
            field_name='funding_amount',
            field_type='funding',
            priority=BackfillPriority.CRITICAL,
            search_strategy='perplexity',
            estimated_cost=0.10
        )
        
        result = await backfill_service._backfill_with_perplexity(job, funding_field)
        
        assert result is not None
        assert result.field_name == 'funding_amount'
        assert result.confidence_score == 0.85
        assert result.data_source == 'perplexity_openai'
        assert result.new_value['amount'] == 250000000
    
    @pytest.mark.asyncio
    async def test_get_backfill_stats(self, backfill_service):
        """Test backfill statistics reporting"""
        
        # Add some mock jobs
        job1 = BackfillJob(
            job_id='job1',
            innovation_id='inn1',
            innovation_title='Test 1',
            innovation_description='Desc 1',
            missing_fields=[],
            status=BackfillStatus.PENDING,
            priority=BackfillPriority.HIGH,
            created_at=datetime.now()
        )
        
        job2 = BackfillJob(
            job_id='job2',
            innovation_id='inn2',
            innovation_title='Test 2',
            innovation_description='Desc 2',
            missing_fields=[],
            status=BackfillStatus.COMPLETED,
            priority=BackfillPriority.HIGH,
            created_at=datetime.now()
        )
        
        backfill_service.job_queue = [job1, job2]
        backfill_service.current_daily_cost = 15.50
        
        stats = backfill_service.get_backfill_stats()
        
        assert stats['total_jobs'] == 2
        assert stats['pending_jobs'] == 1
        assert stats['completed_jobs'] == 1
        assert stats['current_daily_cost'] == 15.50
        assert stats['daily_cost_limit'] == 50.0
        assert stats['cost_utilization'] == 31.0  # 15.50/50.0 * 100


class TestBackfillJobProcessing:
    """Test backfill job processing scenarios"""
    
    @pytest.fixture
    def sample_job(self):
        """Create a sample backfill job"""
        return BackfillJob(
            job_id='test-job-456',
            innovation_id='innovation-789',
            innovation_title='Paystack',
            innovation_description='Nigerian payment processing company',
            missing_fields=[
                MissingField(
                    field_name='funding_amount',
                    field_type='funding',
                    priority=BackfillPriority.CRITICAL,
                    search_strategy='perplexity',
                    estimated_cost=0.10
                ),
                MissingField(
                    field_name='website_url',
                    field_type='urls',
                    priority=BackfillPriority.CRITICAL,
                    search_strategy='serper',
                    estimated_cost=0.05
                )
            ],
            status=BackfillStatus.PENDING,
            priority=BackfillPriority.CRITICAL,
            created_at=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_job_lifecycle(self, sample_job):
        """Test complete job processing lifecycle"""
        
        service = AIBackfillService()
        
        # Mock successful processing
        with patch.object(service, '_backfill_with_perplexity') as mock_perplexity, \
             patch.object(service, '_backfill_with_serper') as mock_serper:
            
            mock_perplexity.return_value = BackfillResult(
                innovation_id='innovation-789',
                field_name='funding_amount',
                old_value=None,
                new_value={'amount': 200000000, 'currency': 'USD'},
                confidence_score=0.8,
                data_source='perplexity_openai',
                validation_status='validated',
                cost=0.10
            )
            
            mock_serper.return_value = BackfillResult(
                innovation_id='innovation-789',
                field_name='website_url',
                old_value=None,
                new_value='https://paystack.com',
                confidence_score=0.9,
                data_source='serper',
                validation_status='validated',
                cost=0.05
            )
            
            processed_job = await service.process_backfill_job(sample_job)
            
            assert processed_job.status == BackfillStatus.COMPLETED
            assert processed_job.total_cost == 0.15
            assert len(processed_job.results) == 2
            assert processed_job.started_at is not None
            assert processed_job.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_job_failure_handling(self, sample_job):
        """Test job failure scenarios"""
        
        service = AIBackfillService()
        
        # Mock API failure
        with patch.object(service, '_backfill_with_perplexity') as mock_perplexity:
            mock_perplexity.side_effect = Exception("API Error")
            
            processed_job = await service.process_backfill_job(sample_job)
            
            assert processed_job.status == BackfillStatus.FAILED
            assert 'API Error' in processed_job.error_message
            assert processed_job.completed_at is not None


class TestIntegrationScenarios:
    """Test integration scenarios with real-world data"""
    
    @pytest.fixture
    def real_world_innovations(self):
        """Real-world innovation examples for testing"""
        return [
            {
                'id': 'flutterwave-001',
                'title': 'Flutterwave',
                'description': 'Payment infrastructure for global merchants and payment service providers',
                'innovation_type': 'FinTech',
                'verification_status': 'verified',
                'fundings': [],
                'website_url': None,
                'organizations': []
            },
            {
                'id': 'mpesa-002',
                'title': 'M-Pesa',
                'description': 'Mobile money transfer service launched by Vodafone',
                'innovation_type': 'FinTech',
                'verification_status': 'verified',
                'fundings': [{'amount': 1000000, 'currency': 'USD'}],  # Has some funding
                'website_url': 'https://mpesa.com',  # Has website
                'organizations': []  # Missing organizations
            }
        ]
    
    @pytest.mark.asyncio
    async def test_batch_job_creation(self, real_world_innovations):
        """Test creating backfill jobs for multiple innovations"""
        
        from services.ai_backfill_service import create_backfill_jobs_for_innovations
        
        with patch('services.ai_backfill_service.ai_backfill_service') as mock_service:
            mock_service.create_backfill_job = AsyncMock()
            mock_service.create_backfill_job.side_effect = [
                BackfillJob(
                    job_id='job1',
                    innovation_id='flutterwave-001',
                    innovation_title='Flutterwave',
                    innovation_description='Payment infrastructure',
                    missing_fields=[],
                    status=BackfillStatus.PENDING,
                    priority=BackfillPriority.CRITICAL,
                    created_at=datetime.now()
                ),
                None  # M-Pesa doesn't need backfilling
            ]
            
            jobs = await create_backfill_jobs_for_innovations(real_world_innovations)
            
            assert len(jobs) == 1
            assert jobs[0].innovation_id == 'flutterwave-001'
    
    @pytest.mark.asyncio
    async def test_prioritization_logic(self):
        """Test that jobs are prioritized correctly"""
        
        service = AIBackfillService()
        
        # Create jobs with different priorities
        high_priority_innovation = {
            'id': 'critical-001',
            'title': 'Critical Innovation',
            'description': 'Verified innovation missing critical data',
            'verification_status': 'verified',
            'fundings': [],  # Missing critical funding info
            'website_url': None,  # Missing critical website
            'organizations': []
        }
        
        low_priority_innovation = {
            'id': 'low-001',
            'title': 'Low Priority Innovation',
            'description': 'Innovation with most data present',
            'verification_status': 'community',
            'fundings': [{'amount': 100000}],  # Has funding
            'website_url': 'https://example.com',  # Has website
            'organizations': [{'name': 'Test Org'}],  # Has org
            'demo_url': None  # Only missing demo URL (low priority)
        }
        
        critical_job = await service.create_backfill_job(high_priority_innovation)
        low_job = await service.create_backfill_job(low_priority_innovation)
        
        assert critical_job.priority == BackfillPriority.CRITICAL
        assert low_job is None or low_job.priority.value > critical_job.priority.value


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])