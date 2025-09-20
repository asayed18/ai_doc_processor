"""
Question service for managing questions and conditions.
"""

from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.database import Question
from ..schemas.schemas import QuestionCreate, QuestionResponse, QuestionUpdate


class QuestionService:
    """Service for managing questions and conditions."""

    def create_question(
        self, question: QuestionCreate, db: Session
    ) -> QuestionResponse:
        """
        Create a new question or condition.

        Args:
            question: Question data
            db: Database session

        Returns:
            Created question response
        """
        db_question = Question(**question.model_dump())
        db.add(db_question)
        db.commit()
        db.refresh(db_question)

        return QuestionResponse.model_validate(db_question)

    def get_questions(
        self, db: Session, question_type: Optional[str] = None, active_only: bool = True
    ) -> List[QuestionResponse]:
        """
        Get all questions, optionally filtered by type.

        Args:
            db: Database session
            question_type: Filter by question type ('question' or 'condition')
            active_only: Only return active questions

        Returns:
            List of question responses
        """
        query = db.query(Question)

        if active_only:
            query = query.filter(Question.is_active == True)

        if question_type:
            query = query.filter(Question.type == question_type)

        questions = query.order_by(Question.created_at.desc()).all()
        return [QuestionResponse.model_validate(q) for q in questions]

    def get_question(self, question_id: int, db: Session) -> Optional[QuestionResponse]:
        """
        Get a specific question by ID.

        Args:
            question_id: The question ID
            db: Database session

        Returns:
            Question response or None if not found
        """
        question = db.query(Question).filter(Question.id == question_id).first()
        if question:
            return QuestionResponse.model_validate(question)
        return None

    def update_question(
        self, question_id: int, question_update: QuestionUpdate, db: Session
    ) -> Optional[QuestionResponse]:
        """
        Update a question.

        Args:
            question_id: The question ID
            question_update: Update data
            db: Database session

        Returns:
            Updated question response or None if not found
        """
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return None

        # Update fields
        update_data = question_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(question, field, value)

        db.commit()
        db.refresh(question)

        return QuestionResponse.model_validate(question)

    def delete_question(self, question_id: int, db: Session) -> bool:
        """
        Delete a question (soft delete by setting is_active=False).

        Args:
            question_id: The question ID
            db: Database session

        Returns:
            True if deleted successfully
        """
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return False

        question.is_active = False
        db.commit()
        return True

    def hard_delete_question(self, question_id: int, db: Session) -> bool:
        """
        Permanently delete a question from database.

        Args:
            question_id: The question ID
            db: Database session

        Returns:
            True if deleted successfully
        """
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return False

        db.delete(question)
        db.commit()
        return True

    def get_questions_by_type(
        self, question_type: str, db: Session
    ) -> List[QuestionResponse]:
        """
        Get questions by specific type.

        Args:
            question_type: 'question' or 'condition'
            db: Database session

        Returns:
            List of question responses
        """
        if question_type not in ["question", "condition"]:
            raise HTTPException(
                status_code=400,
                detail="Question type must be 'question' or 'condition'",
            )

        return self.get_questions(db, question_type=question_type)
