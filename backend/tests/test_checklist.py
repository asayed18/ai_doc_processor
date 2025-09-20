"""
Integration tests for checklist processing functionality.
"""

import io

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestChecklistProcessing:
    """Test checklist processing with mocked AI service."""

    def test_process_checklist_with_files_and_questions(
        self, test_client: TestClient, sample_pdf_content: bytes
    ):
        """Test processing checklist with uploaded files and questions."""
        # Upload test files
        files = {
            "file": ("test1.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        upload_response = test_client.post("/api/v1/files/upload", files=files)
        file_id = upload_response.json()["id"]

        # Process checklist
        checklist_request = {
            "file_ids": [file_id],
            "questions": ["In welcher Form sind die Angebote einzureichen?"],
            "conditions": ["Ist die Abgabefrist vor dem 31.12.2025?"],
        }

        response = test_client.post("/api/v1/checklist/", json=checklist_request)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure (from MockAIService)
        assert "session_id" in data
        assert "question_answers" in data
        assert "condition_evaluations" in data
        assert "processing_time_ms" in data
        assert "files_processed" in data

        # Verify mock responses
        assert data["session_id"] == "mock-session-id"
        assert data["processing_time_ms"] == 100
        assert data["files_processed"] == ["mock-file.pdf"]

        # Verify question answers
        assert len(data["question_answers"]) == 1
        expected_question = "In welcher Form sind die Angebote einzureichen?"
        assert expected_question in data["question_answers"]
        assert (
            data["question_answers"][expected_question]
            == "Mock answer for testing purposes"
        )

        # Verify condition evaluations
        assert len(data["condition_evaluations"]) == 1
        expected_condition = "Ist die Abgabefrist vor dem 31.12.2025?"
        assert expected_condition in data["condition_evaluations"]
        assert data["condition_evaluations"][expected_condition] is True

    def test_process_checklist_questions_only(self, test_client: TestClient):
        """Test processing checklist with questions only (no files)."""
        checklist_request = {
            "file_ids": [],
            "questions": ["What are the main requirements?", "When is the deadline?"],
            "conditions": [],
        }

        response = test_client.post("/api/v1/checklist/", json=checklist_request)

        assert response.status_code == 200
        data = response.json()

        assert len(data["question_answers"]) == 2
        assert len(data["condition_evaluations"]) == 0

        for question in checklist_request["questions"]:
            assert question in data["question_answers"]

    def test_process_checklist_conditions_only(self, test_client: TestClient):
        """Test processing checklist with conditions only."""
        checklist_request = {
            "file_ids": [],
            "questions": [],
            "conditions": [
                "Is the deadline before 2025?",
                "Are electronic submissions allowed?",
            ],
        }

        response = test_client.post("/api/v1/checklist/", json=checklist_request)

        assert response.status_code == 200
        data = response.json()

        assert len(data["question_answers"]) == 0
        assert len(data["condition_evaluations"]) == 2

        for condition in checklist_request["conditions"]:
            assert condition in data["condition_evaluations"]
            assert (
                data["condition_evaluations"][condition] is True
            )  # Mock always returns True

    def test_process_checklist_empty_request(self, test_client: TestClient):
        """Test processing checklist with empty request."""
        checklist_request = {"file_ids": [], "questions": [], "conditions": []}

        response = test_client.post("/api/v1/checklist/", json=checklist_request)

        assert response.status_code == 200
        data = response.json()

        assert len(data["question_answers"]) == 0
        assert len(data["condition_evaluations"]) == 0

    def test_process_checklist_with_multiple_files(
        self, test_client: TestClient, sample_pdf_content: bytes
    ):
        """Test processing checklist with multiple files."""
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

        # Process checklist
        checklist_request = {
            "file_ids": file_ids,
            "questions": ["What are the requirements?"],
            "conditions": ["Is deadline before 2025?"],
        }

        response = test_client.post("/api/v1/checklist/", json=checklist_request)

        assert response.status_code == 200
        data = response.json()

        assert len(data["question_answers"]) == 1
        assert len(data["condition_evaluations"]) == 1

    def test_process_checklist_with_nonexistent_files(self, test_client: TestClient):
        """Test processing checklist with non-existent file IDs."""
        checklist_request = {
            "file_ids": [999, 1000],  # Non-existent file IDs
            "questions": ["What are the requirements?"],
            "conditions": [],
        }

        response = test_client.post("/api/v1/checklist/", json=checklist_request)

        # Should still work with mock service (it doesn't actually process files)
        assert response.status_code == 200

    def test_process_checklist_invalid_request_format(self, test_client: TestClient):
        """Test processing checklist with invalid request format."""
        # Request with invalid data types
        invalid_request = {
            "file_ids": "not a list",  # Should be a list
            "questions": "not a list",  # Should be a list
            "conditions": "not a list",  # Should be a list
        }

        response = test_client.post("/api/v1/checklist/", json=invalid_request)

        assert response.status_code == 422  # Validation error

    def test_process_checklist_large_request(self, test_client: TestClient):
        """Test processing checklist with many questions and conditions."""
        # Create a large number of questions and conditions
        questions = [f"Question {i}?" for i in range(50)]
        conditions = [f"Condition {i} is met?" for i in range(50)]

        checklist_request = {
            "file_ids": [],
            "questions": questions,
            "conditions": conditions,
        }

        response = test_client.post("/api/v1/checklist/", json=checklist_request)

        assert response.status_code == 200
        data = response.json()

        assert len(data["question_answers"]) == 50
        assert len(data["condition_evaluations"]) == 50

    def test_process_checklist_special_characters(self, test_client: TestClient):
        """Test processing checklist with special characters."""
        checklist_request = {
            "file_ids": [],
            "questions": [
                "Frage mit Umlauten: Wie hoch sind die Kosten für die Lösung?",
                "Question with symbols: What's the cost @#$%?",
            ],
            "conditions": [
                "Bedingung mit ß: Die Lösung muß vor 2025 fertig sein",
                "Condition with quotes: The cost is 'acceptable'",
            ],
        }

        response = test_client.post("/api/v1/checklist/", json=checklist_request)

        assert response.status_code == 200
        data = response.json()

        # Verify all questions and conditions are handled
        for question in checklist_request["questions"]:
            assert question in data["question_answers"]

        for condition in checklist_request["conditions"]:
            assert condition in data["condition_evaluations"]


@pytest.mark.integration
class TestChecklistProcessingEdgeCases:
    """Test edge cases for checklist processing."""

    def test_process_checklist_very_long_text(self, test_client: TestClient):
        """Test processing checklist with very long questions and conditions."""
        long_question = "A" * 1000 + " - What are the requirements?"
        long_condition = "B" * 1000 + " - The deadline is before 2025?"

        checklist_request = {
            "file_ids": [],
            "questions": [long_question],
            "conditions": [long_condition],
        }

        response = test_client.post("/api/v1/checklist/", json=checklist_request)

        assert response.status_code == 200
        data = response.json()

        assert long_question in data["question_answers"]
        assert long_condition in data["condition_evaluations"]

    def test_process_checklist_duplicate_questions(self, test_client: TestClient):
        """Test processing checklist with duplicate questions."""
        duplicate_question = "What are the requirements?"

        checklist_request = {
            "file_ids": [],
            "questions": [duplicate_question, duplicate_question],
            "conditions": [],
        }

        response = test_client.post("/api/v1/checklist/", json=checklist_request)

        assert response.status_code == 200
        data = response.json()

        # Mock service should handle duplicates appropriately
        assert duplicate_question in data["question_answers"]

    def test_process_checklist_empty_strings(self, test_client: TestClient):
        """Test processing checklist with empty string questions."""
        checklist_request = {
            "file_ids": [],
            "questions": ["", "Valid question"],
            "conditions": ["", "Valid condition"],
        }

        response = test_client.post("/api/v1/checklist/", json=checklist_request)

        assert response.status_code == 200
        data = response.json()

        # Should handle empty strings gracefully
        assert "Valid question" in data["question_answers"]
        assert "Valid condition" in data["condition_evaluations"]

    def test_process_checklist_concurrent_requests(
        self, test_client: TestClient, sample_pdf_content: bytes
    ):
        """Test concurrent checklist processing requests."""
        import concurrent.futures

        # Upload a test file
        files = {
            "file": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")
        }
        upload_response = test_client.post("/api/v1/files/upload", files=files)
        file_id = upload_response.json()["id"]

        def process_checklist(request_id: int):
            checklist_request = {
                "file_ids": [file_id],
                "questions": [f"Question {request_id}?"],
                "conditions": [f"Condition {request_id} is met?"],
            }
            return test_client.post("/api/v1/checklist/", json=checklist_request)

        # Submit concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(process_checklist, i) for i in range(5)]

            responses = [future.result() for future in futures]

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "question_answers" in data
            assert "condition_evaluations" in data
