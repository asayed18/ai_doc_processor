"""
Integration tests for chat functionality.
"""

import io

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestChatFunctionality:
    """Test chat endpoints with mocked AI service."""

    def test_chat_with_files(self, test_client: TestClient, sample_pdf_content: bytes):
        """Test chat functionality with uploaded files."""
        # Upload test files
        files = {
            "file": ("test1.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        upload_response = test_client.post("/api/v1/files/upload", files=files)
        file_id = upload_response.json()["id"]

        # Send chat request
        chat_request = {
            "message": "What are the main requirements in these documents?",
            "file_ids": [file_id],
        }

        response = test_client.post("/api/v1/checklist/chat", json=chat_request)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure (from MockAIService)
        assert "response" in data
        assert "files_used" in data

        # Verify mock responses
        expected_response = f"Mock response to: {chat_request['message']}"
        assert data["response"] == expected_response
        assert data["files_used"] == ["mock-file.pdf"]

    def test_chat_without_files(self, test_client: TestClient):
        """Test chat functionality without files."""
        chat_request = {
            "message": "What are general best practices for tender documents?",
            "file_ids": [],
        }

        response = test_client.post("/api/v1/checklist/chat", json=chat_request)

        assert response.status_code == 200
        data = response.json()

        assert "response" in data
        expected_response = f"Mock response to: {chat_request['message']}"
        assert data["response"] == expected_response

    def test_chat_with_multiple_files(
        self, test_client: TestClient, sample_pdf_content: bytes
    ):
        """Test chat functionality with multiple files."""
        # Upload multiple test files
        file_ids = []
        for i in range(3):
            files = {
                "file": (
                    f"test{i}.pdf",
                    io.BytesIO(sample_pdf_content),
                    "application/pdf",
                )
            }
            upload_response = test_client.post("/api/v1/files/upload", files=files)
            file_ids.append(upload_response.json()["id"])

        # Send chat request
        chat_request = {
            "message": "Compare the requirements across these documents",
            "file_ids": file_ids,
        }

        response = test_client.post("/api/v1/checklist/chat", json=chat_request)

        assert response.status_code == 200
        data = response.json()

        assert "response" in data
        expected_response = f"Mock response to: {chat_request['message']}"
        assert data["response"] == expected_response

    def test_chat_with_nonexistent_files(self, test_client: TestClient):
        """Test chat functionality with non-existent file IDs."""
        chat_request = {
            "message": "What information can you find?",
            "file_ids": [999, 1000],  # Non-existent file IDs
        }

        response = test_client.post("/api/v1/checklist/chat", json=chat_request)

        # Should still work with mock service (it doesn't actually process files)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

    def test_chat_empty_message(self, test_client: TestClient):
        """Test chat functionality with empty message."""
        chat_request = {"message": "", "file_ids": []}

        response = test_client.post("/api/v1/checklist/chat", json=chat_request)

        assert response.status_code == 200
        data = response.json()

        # Mock service should handle empty messages
        assert data["response"] == "Mock response to: "

    def test_chat_long_message(self, test_client: TestClient):
        """Test chat functionality with very long message."""
        long_message = "A" * 1000 + " What are the requirements?"

        chat_request = {"message": long_message, "file_ids": []}

        response = test_client.post("/api/v1/checklist/chat", json=chat_request)

        assert response.status_code == 200
        data = response.json()

        expected_response = f"Mock response to: {long_message}"
        assert data["response"] == expected_response

    def test_chat_special_characters(self, test_client: TestClient):
        """Test chat functionality with special characters."""
        special_message = "Frage mit Umlauten: Wie hoch sind die Kosten? !@#$%^&*()"

        chat_request = {"message": special_message, "file_ids": []}

        response = test_client.post("/api/v1/checklist/chat", json=chat_request)

        assert response.status_code == 200
        data = response.json()

        expected_response = f"Mock response to: {special_message}"
        assert data["response"] == expected_response

    def test_chat_invalid_request_format(self, test_client: TestClient):
        """Test chat functionality with invalid request format."""
        # Missing required message field
        invalid_request = {
            "file_ids": []
            # Missing message
        }

        response = test_client.post("/api/v1/checklist/chat", json=invalid_request)

        assert response.status_code == 422  # Validation error

    def test_chat_invalid_file_ids_format(self, test_client: TestClient):
        """Test chat functionality with invalid file IDs format."""
        chat_request = {
            "message": "Test message",
            "file_ids": ["not", "integers"],  # Should be integers
        }

        response = test_client.post("/api/v1/checklist/chat", json=chat_request)

        assert response.status_code == 422  # Validation error

    def test_chat_mixed_content_types(self, test_client: TestClient):
        """Test chat with various message types."""
        messages = [
            "What are the requirements?",
            "How much does it cost?",
            "When is the deadline?",
            "Are there any restrictions?",
            "What documents are needed?",
        ]

        for message in messages:
            chat_request = {"message": message, "file_ids": []}

            response = test_client.post("/api/v1/checklist/chat", json=chat_request)

            assert response.status_code == 200
            data = response.json()

            expected_response = f"Mock response to: {message}"
            assert data["response"] == expected_response


@pytest.mark.integration
class TestChatPerformance:
    """Performance tests for chat functionality."""

    def test_chat_concurrent_requests(self, test_client: TestClient):
        """Test concurrent chat requests."""
        import concurrent.futures

        def send_chat_request(request_id: int):
            chat_request = {"message": f"Chat message {request_id}", "file_ids": []}
            return test_client.post("/api/v1/checklist/chat", json=chat_request)

        # Submit concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(send_chat_request, i) for i in range(5)]

            responses = [future.result() for future in futures]

        # All requests should succeed
        for i, response in enumerate(responses):
            assert response.status_code == 200
            data = response.json()
            expected_response = f"Mock response to: Chat message {i}"
            assert data["response"] == expected_response

    @pytest.mark.slow
    def test_chat_rapid_sequential_requests(self, test_client: TestClient):
        """Test rapid sequential chat requests."""
        for i in range(20):
            chat_request = {"message": f"Rapid message {i}", "file_ids": []}

            response = test_client.post("/api/v1/checklist/chat", json=chat_request)

            assert response.status_code == 200
            data = response.json()
            expected_response = f"Mock response to: Rapid message {i}"
            assert data["response"] == expected_response


@pytest.mark.integration
class TestChatIntegrationWithFiles:
    """Test chat integration with file management."""

    def test_chat_after_file_upload_and_delete(
        self, test_client: TestClient, sample_pdf_content: bytes
    ):
        """Test chat functionality after uploading and deleting files."""
        # Upload a file
        files = {
            "file": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        upload_response = test_client.post("/api/v1/files/upload", files=files)
        file_id = upload_response.json()["id"]

        # Chat with the file
        chat_request = {"message": "What's in this document?", "file_ids": [file_id]}

        response = test_client.post("/api/v1/checklist/chat", json=chat_request)
        assert response.status_code == 200

        # Delete the file
        delete_response = test_client.delete(f"/api/v1/files/{file_id}")
        assert delete_response.status_code == 200

        # Try to chat with the deleted file
        response = test_client.post("/api/v1/checklist/chat", json=chat_request)

        # Should still work with mock service (doesn't actually check file existence)
        assert response.status_code == 200

    def test_chat_workflow_with_multiple_operations(
        self, test_client: TestClient, sample_pdf_content: bytes
    ):
        """Test complete workflow: upload files, chat, process checklist."""
        # Upload files
        file_ids = []
        for i in range(2):
            files = {
                "file": (
                    f"workflow{i}.pdf",
                    io.BytesIO(sample_pdf_content),
                    "application/pdf",
                )
            }
            upload_response = test_client.post("/api/v1/files/upload", files=files)
            file_ids.append(upload_response.json()["id"])

        # Chat about the files
        chat_request = {
            "message": "What are the main topics in these documents?",
            "file_ids": file_ids,
        }

        chat_response = test_client.post("/api/v1/checklist/chat", json=chat_request)
        assert chat_response.status_code == 200

        # Process checklist with the same files
        checklist_request = {
            "file_ids": file_ids,
            "questions": ["What are the requirements?"],
            "conditions": ["Is the deadline before 2025?"],
        }

        checklist_response = test_client.post(
            "/api/v1/checklist/", json=checklist_request
        )
        assert checklist_response.status_code == 200

        # Both operations should work independently
        chat_data = chat_response.json()
        checklist_data = checklist_response.json()

        assert "response" in chat_data
        assert "question_answers" in checklist_data
        assert "condition_evaluations" in checklist_data
