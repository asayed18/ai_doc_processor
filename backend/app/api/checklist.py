"""
AI-powered checklist processing API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import (
    ChatRequest,
    ChatResponse,
    ChecklistRequest,
    ChecklistResult,
)
from app.services.ai_factory import get_ai_service
from app.services.ai_service import AIService

router = APIRouter(prefix="/checklist", tags=["checklist"])


@router.post("/", response_model=ChecklistResult)
def process_checklist(
    request: ChecklistRequest,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
):
    """Process a checklist of questions and conditions against uploaded documents."""
    return ai_service.process_checklist(request, db)


@router.post("/chat", response_model=ChatResponse)
def chat_with_documents(
    request: ChatRequest,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
):
    """Chat with AI using uploaded documents as context."""
    result = ai_service.chat_with_documents(request.message, request.file_ids, db)
    return ChatResponse(response=result["response"], files_used=result["files_used"])
