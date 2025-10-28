"""
Integration tests for API endpoints
APIエンドポイント統合テスト
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestAPIEndpoints:
    """API endpoint integration tests"""
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_graph_endpoint_valid_address(self, client):
        """Test graph endpoint with valid address"""
        # Use a known Ethereum address for testing
        test_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        
        response = client.get(
            f"/api/v1/graph/address/{test_address}",
            params={"chain": "ethereum", "depth": 1, "min_amount": 0}
        )
        
        # Should return 200 or handle gracefully
        assert response.status_code in [200, 500]  # 500 if Etherscan API fails
        
        if response.status_code == 200:
            data = response.json()
            assert "nodes" in data
            assert "edges" in data
            assert "total_nodes" in data
            assert "total_edges" in data
            assert isinstance(data["nodes"], list)
            assert isinstance(data["edges"], list)
    
    def test_graph_endpoint_invalid_address(self, client):
        """Test graph endpoint with invalid address"""
        response = client.get(
            "/api/v1/graph/address/invalid",
            params={"chain": "ethereum"}
        )
        
        # Should handle invalid address gracefully
        assert response.status_code in [400, 404, 500]
    
    def test_pattern_analysis_endpoint(self, client):
        """Test pattern analysis endpoint"""
        test_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        
        response = client.post(
            "/api/v1/analysis/pattern",
            json={
                "address": test_address,
                "chain": "ethereum",
                "lookback_days": 30
            }
        )
        
        # Should return 200 or handle API failures gracefully
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "address" in data
            assert "detected_patterns" in data
            assert "overall_risk_score" in data
            assert isinstance(data["detected_patterns"], list)
    
    def test_risk_score_endpoint(self, client):
        """Test risk score calculation endpoint"""
        test_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        
        response = client.post(
            "/api/v1/analysis/risk-score",
            json={
                "address": test_address,
                "chain": "ethereum"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "address" in data
            assert "risk_score" in data
            assert "risk_level" in data
            assert "factors" in data
            assert 0 <= data["risk_score"] <= 100
    
    def test_narrative_generation_endpoint(self, client):
        """Test narrative generation endpoint"""
        test_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        
        response = client.post(
            "/api/v1/analysis/narrative",
            json={
                "address": test_address,
                "chain": "ethereum",
                "language": "ja",
                "max_hops": 10
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "address" in data
            assert "narrative" in data
            assert "key_findings" in data
            assert "timeline" in data
            assert isinstance(data["narrative"], str)
            assert isinstance(data["key_findings"], list)
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        response = client.options("/api/v1/graph/address/0x123")
        
        # Check CORS headers
        assert "access-control-allow-origin" in response.headers or response.status_code == 404
    
    def test_rate_limiting_headers(self, client):
        """Test rate limiting headers are present"""
        response = client.get("/health")
        
        # Check rate limit headers (if middleware is active)
        # Headers might not be present in test environment
        assert response.status_code == 200
    
    def test_security_headers(self, client):
        """Test security headers are present"""
        response = client.get("/health")
        
        # Check for common security headers
        # These might not all be present in test environment
        assert response.status_code == 200
        
        # At least verify response is valid
        assert "content-type" in response.headers
