"""
Question management API routes.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..schemas.schemas import QuestionCreate, QuestionResponse, QuestionUpdate
from ..services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["questions"])
question_service = QuestionService()


@router.post("/", response_model=QuestionResponse)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    """Create a new question or condition."""
    return question_service.create_question(question, db)


@router.get("/", response_model=List[QuestionResponse])
def get_questions(
    question_type: Optional[str] = Query(None, pattern="^(question|condition)$"),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Get all questions, optionally filtered by type."""
    return question_service.get_questions(db, question_type, active_only)


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    """Get a specific question by ID."""
    question = question_service.get_question(question_id, db)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int, question_update: QuestionUpdate, db: Session = Depends(get_db)
):
    """Update a question."""
    question = question_service.update_question(question_id, question_update, db)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """Delete a question (soft delete)."""
    success = question_service.delete_question(question_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}


@router.delete("/{question_id}/hard")
def hard_delete_question(question_id: int, db: Session = Depends(get_db)):
    """Permanently delete a question."""
    success = question_service.hard_delete_question(question_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question permanently deleted"}
