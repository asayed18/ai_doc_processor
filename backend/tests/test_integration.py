"""
Test runner for comprehensive integration tests.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_api_root_endpoint(test_client: TestClient):
    """Test that the API root endpoint is accessible."""
    response = test_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.integration
def test_api_docs_accessible(test_client: TestClient):
    """Test that the API documentation is accessible."""
    response = test_client.get("/docs")

    assert response.status_code == 200
    # Should return HTML content for the docs
    assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.integration
def test_openapi_spec_accessible(test_client: TestClient):
    """Test that the OpenAPI specification is accessible."""
    response = test_client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()

    # Verify basic OpenAPI structure
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data


@pytest.mark.integration
def test_health_check_endpoints(test_client: TestClient):
    """Test health check and debug endpoints."""
    # Test root endpoint
    response = test_client.get("/")
    assert response.status_code == 200

    # Test if debug endpoint exists (might be environment dependent)
    debug_response = test_client.get("/debug")
    # Debug endpoint might not exist in all configurations
    assert debug_response.status_code in [200, 404]


@pytest.mark.integration
def test_cors_configuration(test_client: TestClient):
    """Test CORS configuration."""
    # Test a preflight request
    response = test_client.options(
        "/api/v1/files/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    # Should allow the request (status might vary based on CORS config)
    assert response.status_code in [200, 204]


@pytest.mark.integration
class TestAPIIntegration:
    """Full API integration tests."""

    def test_complete_file_workflow(
        self, test_client: TestClient, sample_pdf_content: bytes
    ):
        """Test complete workflow: upload -> list -> process -> delete."""
        import io

        # 1. Upload a file
        files = {
            "file": (
                "integration_test.pdf",
                io.BytesIO(sample_pdf_content),
                "application/pdf",
            )
        }
        upload_response = test_client.post("/api/v1/files/upload", files=files)
        assert upload_response.status_code == 200
        file_id = upload_response.json()["id"]

        # 2. List files and verify upload
        list_response = test_client.get("/api/v1/files/")
        assert list_response.status_code == 200
        files_list = list_response.json()
        assert len(files_list) >= 1
        assert any(f["id"] == file_id for f in files_list)

        # 3. Create questions
        question_data = {"text": "Integration test question", "type": "question"}
        question_response = test_client.post("/api/v1/questions/", json=question_data)
        assert question_response.status_code == 200
        question_id = question_response.json()["id"]

        # 4. Process checklist
        checklist_request = {
            "file_ids": [file_id],
            "questions": ["Integration test question"],
            "conditions": ["Integration test condition"],
        }
        checklist_response = test_client.post(
            "/api/v1/checklist/", json=checklist_request
        )
        assert checklist_response.status_code == 200
        checklist_data = checklist_response.json()
        assert "question_answers" in checklist_data
        assert "condition_evaluations" in checklist_data

        # 5. Test chat functionality
        chat_request = {
            "message": "Integration test chat message",
            "file_ids": [file_id],
        }
        chat_response = test_client.post("/api/v1/checklist/chat", json=chat_request)
        assert chat_response.status_code == 200
        chat_data = chat_response.json()
        assert "response" in chat_data

        # 6. Clean up - delete question and file
        delete_question_response = test_client.delete(
            f"/api/v1/questions/{question_id}"
        )
        assert delete_question_response.status_code == 200

        delete_file_response = test_client.delete(f"/api/v1/files/{file_id}")
        assert delete_file_response.status_code == 200

        # 7. Verify cleanup
        final_list_response = test_client.get("/api/v1/files/")
        final_files = final_list_response.json()
        assert not any(f["id"] == file_id for f in final_files)

    def test_error_handling(self, test_client: TestClient):
        """Test API error handling."""
        # Test 404 errors
        response = test_client.get("/api/v1/files/999999")
        assert response.status_code == 404

        response = test_client.delete("/api/v1/files/999999")
        assert response.status_code == 404

        response = test_client.delete("/api/v1/questions/999999")
        assert response.status_code == 404

        # Test validation errors
        invalid_question = {"text": ""}  # Missing type
        response = test_client.post("/api/v1/questions/", json=invalid_question)
        assert response.status_code == 422

        invalid_checklist = {"file_ids": "not_a_list"}  # Invalid type
        response = test_client.post("/api/v1/checklist/", json=invalid_checklist)
        assert response.status_code == 422

    def test_api_versioning(self, test_client: TestClient):
        """Test that API versioning is working correctly."""
        # All main endpoints should be under /api/v1/
        endpoints_to_test = [
            "/api/v1/files/",
            "/api/v1/questions/",
            "/api/v1/checklist/",
        ]

        for endpoint in endpoints_to_test:
            response = test_client.get(endpoint)
            # Should not get 404 (endpoint exists)
            assert response.status_code != 404
