"""
Integration tests for ML pipeline
ML パイプライン統合テスト
"""

import pytest
from app.services.ml.pattern_matcher import PatternMatcher
from app.services.ml.anomaly_detector import AnomalyDetector
from app.services.ml.risk_scorer import RiskScorer
from app.services.narrative.narrative_generator import NarrativeGenerator


class TestMLPipeline:
    """ML pipeline integration tests"""
    
    @pytest.fixture
    def sample_transactions(self):
        """Sample transaction data for testing"""
        return [
            {
                "hash": "0x123",
                "from": "0xaaa",
                "to": "0xbbb",
                "value": 0.5,
                "timestamp": "2024-01-01T10:00:00Z"
            },
            {
                "hash": "0x124",
                "from": "0xaaa",
                "to": "0xccc",
                "value": 0.3,
                "timestamp": "2024-01-01T10:15:00Z"
            },
            {
                "hash": "0x125",
                "from": "0xaaa",
                "to": "0xddd",
                "value": 0.4,
                "timestamp": "2024-01-01T10:30:00Z"
            },
        ]
    
    def test_pattern_detection(self, sample_transactions):
        """Test pattern detection functionality"""
        matcher = PatternMatcher()
        patterns = matcher.detect_patterns(sample_transactions, "0xaaa")
        
        assert isinstance(patterns, list)
        # Should detect patterns with enough transactions
        for pattern in patterns:
            assert "pattern_id" in pattern
            assert "confidence" in pattern
            assert 0 <= pattern["confidence"] <= 1
    
    def test_anomaly_detection(self, sample_transactions):
        """Test anomaly detection functionality"""
        detector = AnomalyDetector()
        anomalies = detector.detect_anomalies(sample_transactions, "0xaaa")
        
        assert isinstance(anomalies, list)
        for anomaly in anomalies:
            assert "anomaly_type" in anomaly
            assert "severity" in anomaly
            assert anomaly["severity"] in ["low", "medium", "high"]
    
    def test_risk_scoring(self, sample_transactions):
        """Test risk scoring functionality"""
        matcher = PatternMatcher()
        detector = AnomalyDetector()
        scorer = RiskScorer()
        
        patterns = matcher.detect_patterns(sample_transactions, "0xaaa")
        anomalies = detector.detect_anomalies(sample_transactions, "0xaaa")
        
        risk_assessment = scorer.calculate_risk_score(
            address="0xaaa",
            transactions=sample_transactions,
            detected_patterns=patterns,
            detected_anomalies=anomalies
        )
        
        assert "risk_score" in risk_assessment
        assert "risk_level" in risk_assessment
        assert 0 <= risk_assessment["risk_score"] <= 100
        assert risk_assessment["risk_level"] in ["critical", "high", "medium", "low", "minimal"]
    
    def test_narrative_generation(self, sample_transactions):
        """Test narrative generation functionality"""
        matcher = PatternMatcher()
        detector = AnomalyDetector()
        scorer = RiskScorer()
        generator = NarrativeGenerator()
        
        patterns = matcher.detect_patterns(sample_transactions, "0xaaa")
        anomalies = detector.detect_anomalies(sample_transactions, "0xaaa")
        risk_assessment = scorer.calculate_risk_score(
            address="0xaaa",
            transactions=sample_transactions,
            detected_patterns=patterns,
            detected_anomalies=anomalies
        )
        
        # Test Japanese narrative
        narrative_ja = generator.generate_narrative(
            address="0xaaa",
            transactions=sample_transactions,
            detected_patterns=patterns,
            detected_anomalies=anomalies,
            risk_assessment=risk_assessment,
            language="ja"
        )
        
        assert isinstance(narrative_ja, str)
        assert len(narrative_ja) > 0
        
        # Test English narrative
        narrative_en = generator.generate_narrative(
            address="0xaaa",
            transactions=sample_transactions,
            detected_patterns=patterns,
            detected_anomalies=anomalies,
            risk_assessment=risk_assessment,
            language="en"
        )
        
        assert isinstance(narrative_en, str)
        assert len(narrative_en) > 0
    
    def test_full_ml_pipeline(self, sample_transactions):
        """Test complete ML pipeline end-to-end"""
        # Initialize all components
        matcher = PatternMatcher()
        detector = AnomalyDetector()
        scorer = RiskScorer()
        generator = NarrativeGenerator()
        
        # Run full pipeline
        patterns = matcher.detect_patterns(sample_transactions, "0xaaa")
        anomalies = detector.detect_anomalies(sample_transactions, "0xaaa")
        risk_assessment = scorer.calculate_risk_score(
            address="0xaaa",
            transactions=sample_transactions,
            detected_patterns=patterns,
            detected_anomalies=anomalies
        )
        narrative = generator.generate_narrative(
            address="0xaaa",
            transactions=sample_transactions,
            detected_patterns=patterns,
            detected_anomalies=anomalies,
            risk_assessment=risk_assessment,
            language="ja"
        )
        
        # Verify all components produced results
        assert isinstance(patterns, list)
        assert isinstance(anomalies, list)
        assert isinstance(risk_assessment, dict)
        assert isinstance(narrative, str)
        
        # Verify data consistency
        assert "risk_score" in risk_assessment
        assert "risk_level" in risk_assessment
        assert len(narrative) > 50  # Meaningful narrative length
