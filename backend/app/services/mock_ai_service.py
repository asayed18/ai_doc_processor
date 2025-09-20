"""
Mock AI service for testing purposes.
"""

from typing import Dict, List

from sqlalchemy.orm import Session

from ..schemas.schemas import ChecklistRequest, ChecklistResult
from .ai_service import AIService


class MockAIService(AIService):
    """Mock AI service for testing."""

    def process_checklist(
        self, request: ChecklistRequest, db: Session
    ) -> ChecklistResult:
        """
        Mock implementation that returns sample responses.

        Args:
            request: The checklist request
            db: Database session

        Returns:
            Mock ChecklistResult
        """
        # Mock responses for testing
        mock_answers = {}
        mock_evaluations = {}

        if request.questions:
            for question in request.questions:
                mock_answers[question] = "Mock answer for testing purposes"

        if request.conditions:
            for condition in request.conditions:
                mock_evaluations[condition] = True

        return ChecklistResult(
            session_id="mock-session-id",
            question_answers=mock_answers,
            condition_evaluations=mock_evaluations,
            processing_time_ms=100,
            files_processed=["mock-file.pdf"],
        )

    def chat_with_documents(
        self, message: str, file_ids: List[int], db: Session
    ) -> Dict[str, str]:
        """
        Mock implementation for chat functionality.

        Args:
            message: User message
            file_ids: List of file IDs
            db: Database session

        Returns:
            Mock response dictionary
        """
        return {
            "response": f"Mock response to: {message}",
            "files_used": ["mock-file.pdf"],
        }
