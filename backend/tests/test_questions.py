"""
Integration tests for question and condition management.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.database import Question


@pytest.mark.integration
class TestQuestionManagement:
    """Test question and condition CRUD operations."""

    def test_create_question(self, test_client: TestClient):
        """Test creating a new question."""
        question_data = {
            "text": "In welcher Form sind die Angebote einzureichen?",
            "type": "question",
        }

        response = test_client.post("/api/v1/questions/", json=question_data)

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["text"] == question_data["text"]
        assert data["type"] == question_data["type"]
        assert data["is_active"] is True

    def test_create_condition(self, test_client: TestClient):
        """Test creating a new condition."""
        condition_data = {
            "text": "Ist die Abgabefrist vor dem 31.12.2025?",
            "type": "condition",
        }

        response = test_client.post("/api/v1/questions/", json=condition_data)

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["text"] == condition_data["text"]
        assert data["type"] == condition_data["type"]
        assert data["is_active"] is True

    def test_create_question_invalid_type(self, test_client: TestClient):
        """Test creating a question with invalid type."""
        question_data = {"text": "Test question", "type": "invalid_type"}

        response = test_client.post("/api/v1/questions/", json=question_data)

        assert response.status_code == 422  # Validation error

    def test_create_question_empty_text(self, test_client: TestClient):
        """Test creating a question with empty text."""
        question_data = {"text": "", "type": "question"}

        response = test_client.post("/api/v1/questions/", json=question_data)

        assert response.status_code == 422  # Validation error

    def test_create_question_missing_fields(self, test_client: TestClient):
        """Test creating a question with missing required fields."""
        question_data = {
            "text": "Test question"
            # Missing 'type' field
        }

        response = test_client.post("/api/v1/questions/", json=question_data)

        assert response.status_code == 422  # Validation error

    def test_get_questions_empty(self, test_client: TestClient):
        """Test getting questions when none exist."""
        response = test_client.get("/api/v1/questions/")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_questions_after_creation(
        self, test_client: TestClient, sample_questions: list[dict]
    ):
        """Test getting questions after creating some."""
        # Create questions
        created_questions = []
        for question_data in sample_questions:
            response = test_client.post("/api/v1/questions/", json=question_data)
            assert response.status_code == 200
            created_questions.append(response.json())

        # Get all questions
        response = test_client.get("/api/v1/questions/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(sample_questions)

        # Verify questions are returned (order might be different due to sorting)
        question_texts = [q["text"] for q in data]
        for expected_question in sample_questions:
            assert expected_question["text"] in question_texts

    def test_get_questions_by_type(
        self,
        test_client: TestClient,
        sample_questions: list[dict],
        sample_conditions: list[dict],
    ):
        """Test filtering questions by type."""
        # Create questions and conditions
        for question_data in sample_questions:
            response = test_client.post("/api/v1/questions/", json=question_data)
            assert response.status_code == 200

        for condition_data in sample_conditions:
            response = test_client.post("/api/v1/questions/", json=condition_data)
            assert response.status_code == 200

        # Get questions by type
        questions_response = test_client.get("/api/v1/questions/?type=question")
        conditions_response = test_client.get("/api/v1/questions/?type=condition")

        assert questions_response.status_code == 200
        assert conditions_response.status_code == 200

    def test_update_question(self, test_client: TestClient):
        """Test updating a question."""
        # Create a question first
        original_data = {"text": "Original question text", "type": "question"}
        create_response = test_client.post("/api/v1/questions/", json=original_data)
        question_id = create_response.json()["id"]

        # Update the question
        updated_data = {
            "text": "Updated question text",
            "type": "question",
            "is_active": False,
        }

        response = test_client.put(
            f"/api/v1/questions/{question_id}", json=updated_data
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == question_id
        assert data["text"] == updated_data["text"]
        assert data["is_active"] == updated_data["is_active"]

    def test_update_nonexistent_question(self, test_client: TestClient):
        """Test updating a question that doesn't exist."""
        updated_data = {"text": "Updated question text", "type": "question"}

        response = test_client.put("/api/v1/questions/999", json=updated_data)

        assert response.status_code == 404

    def test_delete_question(self, test_client: TestClient):
        """Test deleting a question."""
        # Create a question first
        question_data = {"text": "Question to be deleted", "type": "question"}
        create_response = test_client.post("/api/v1/questions/", json=question_data)
        question_id = create_response.json()["id"]

        # Delete the question
        response = test_client.delete(f"/api/v1/questions/{question_id}")

        assert response.status_code == 200
        assert response.json()["message"] == "Question deleted successfully"

        # Verify question is gone
        get_response = test_client.get("/api/v1/questions/")
        questions = get_response.json()
        question_ids = [q["id"] for q in questions]
        assert question_id not in question_ids

    def test_delete_nonexistent_question(self, test_client: TestClient):
        """Test deleting a question that doesn't exist."""
        response = test_client.delete("/api/v1/questions/999")

        assert response.status_code == 404

    def test_question_persistence(self, test_client: TestClient):
        """Test that questions persist between requests."""
        # Create a question
        question_data = {"text": "Persistent question", "type": "question"}
        create_response = test_client.post("/api/v1/questions/", json=question_data)
        question_id = create_response.json()["id"]

        # Make multiple requests to verify persistence
        for _ in range(3):
            response = test_client.get("/api/v1/questions/")
            questions = response.json()
            question_ids = [q["id"] for q in questions]
            assert question_id in question_ids

    def test_bulk_question_operations(self, test_client: TestClient):
        """Test bulk operations with multiple questions."""
        # Create multiple questions
        questions_data = [
            {"text": f"Question {i}", "type": "question"} for i in range(10)
        ]

        created_ids = []
        for question_data in questions_data:
            response = test_client.post("/api/v1/questions/", json=question_data)
            assert response.status_code == 200
            created_ids.append(response.json()["id"])

        # Verify all questions exist
        response = test_client.get("/api/v1/questions/")
        assert len(response.json()) == 10

        # Delete all questions
        for question_id in created_ids:
            delete_response = test_client.delete(f"/api/v1/questions/{question_id}")
            assert delete_response.status_code == 200

        # Verify all questions are deleted
        response = test_client.get("/api/v1/questions/")
        assert len(response.json()) == 0


@pytest.mark.integration
class TestQuestionValidation:
    """Test question validation logic."""

    @pytest.mark.parametrize("question_type", ["question", "condition"])
    def test_valid_question_types(self, test_client: TestClient, question_type: str):
        """Test that valid question types are accepted."""
        question_data = {"text": f"Test {question_type}", "type": question_type}

        response = test_client.post("/api/v1/questions/", json=question_data)
        assert response.status_code == 200

    @pytest.mark.parametrize("invalid_type", ["invalid", "QUESTION", "Question", ""])
    def test_invalid_question_types(self, test_client: TestClient, invalid_type: str):
        """Test that invalid question types are rejected."""
        question_data = {"text": "Test question", "type": invalid_type}

        response = test_client.post("/api/v1/questions/", json=question_data)
        assert response.status_code == 422

    def test_question_text_length_limits(self, test_client: TestClient):
        """Test question text length validation."""
        # Test very long text
        long_text = "A" * 10000  # Very long question
        question_data = {"text": long_text, "type": "question"}

        response = test_client.post("/api/v1/questions/", json=question_data)
        # Should still accept long text (no explicit limit in current implementation)
        assert response.status_code == 200

    def test_special_characters_in_question(self, test_client: TestClient):
        """Test questions with special characters."""
        special_text = "Frage mit Umlauten: ÄÖÜäöüß und Zeichen: !@#$%^&*()?"
        question_data = {"text": special_text, "type": "question"}

        response = test_client.post("/api/v1/questions/", json=question_data)
        assert response.status_code == 200

        data = response.json()
        assert data["text"] == special_text
