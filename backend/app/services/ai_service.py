"""
Abstract base class for AI services.
"""

from abc import ABC, abstractmethod
from typing import Dict, List

from sqlalchemy.orm import Session

from ..schemas.schemas import ChecklistRequest, ChecklistResult


class AIService(ABC):
    """Abstract base class for AI services."""

    @abstractmethod
    def process_checklist(
        self, request: ChecklistRequest, db: Session
    ) -> ChecklistResult:
        """
        Process a checklist request against uploaded documents.

        Args:
            request: The checklist request containing questions, conditions, and file IDs
            db: Database session

        Returns:
            ChecklistResult with answers and evaluations
        """
        raise NotImplementedError

    @abstractmethod
    def chat_with_documents(
        self, message: str, file_ids: List[int], db: Session
    ) -> Dict[str, str]:
        """
        Chat with AI using documents as context.

        Args:
            message: User message
            file_ids: List of file IDs to use as context
            db: Database session

        Returns:
            Dictionary with response and files used
        """
        raise NotImplementedError
