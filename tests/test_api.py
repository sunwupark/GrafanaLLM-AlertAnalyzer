"""
API Endpoint Test
"""
from fastapi.testclient import TestClient
import pytest
import sys
from unittest.mock import AsyncMock, MagicMock

mock_alert_analyzer = MagicMock()
mock_alert_analyzer.analyze_alert = AsyncMock(return_value={
    "status": "success",
    "analysis": {
        "problem": "Test problem",
        "cause": "Test cause",
        "solution": "Test solution"
    },
    "raw_response": "Test raw response"
})
sys.modules["app.services.alert_analyzer"] = mock_alert_analyzer

mock_notification = MagicMock()
mock_notification.send_email_alert = MagicMock(return_value=None)
sys.modules["app.services.notification"] = mock_notification

from app.api.endpoints import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_alert_endpoint_with_valid_data():
    test_alert_data = {
        "alerts": [
            {
                "annotations": {
                    "description": "Test alert description",
                    "summary": "Test alert summary"
                }
            }
        ]
    }
    
    response = client.post("/alert", json=test_alert_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "analysis" in data
    assert data["analysis"]["problem"] == "Test problem"
    assert data["analysis"]["cause"] == "Test cause"
    assert data["analysis"]["solution"] == "Test solution"
    
    mock_alert_analyzer.analyze_alert.assert_called_once_with("Test alert description")