"""
Simple test to debug which AI service is being used.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_which_service_used(test_client: TestClient, mock_ai_service):
    """Test to see which service is actually being used."""

    # Try a simple checklist request
    checklist_request = {
        "file_ids": [],
        "questions": ["Test question"],
        "conditions": [],
    }

    response = test_client.post("/api/v1/checklist/", json=checklist_request)

    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Session ID: {data.get('session_id')}")
        # Mock service should return "mock-session-id"
        assert (
            data.get("session_id") == "mock-session-id"
        ), f"Expected mock-session-id but got {data.get('session_id')}"
    else:
        print(f"Response content: {response.content}")
