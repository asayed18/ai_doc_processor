"""
Claude AI service for document processing and analysis.
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import anthropic
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.database import File, ProcessingSession, Question
from ..schemas.schemas import ChecklistRequest, ChecklistResult
from ..services.file_service import FileService
from .ai_service import AIService


class ClaudeService(AIService):
    """Service for interacting with Claude AI."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.file_service = FileService()

    def process_checklist(
        self, request: ChecklistRequest, db: Session
    ) -> ChecklistResult:
        """
        Process a checklist request using Claude AI.

        Args:
            request: The checklist request
            db: Database session

        Returns:
            ChecklistResult with processed answers
        """
        start_time = time.time()
        session_id = str(uuid.uuid4())

        try:
            # Create processing session
            session = ProcessingSession(
                session_id=session_id,
                file_ids=json.dumps(request.file_ids),
                question_ids=json.dumps(request.question_ids or []),
                status="processing",
            )
            db.add(session)
            db.commit()

            # Get document content
            document_content = self._extract_document_content(request.file_ids, db)

            # Get questions and conditions
            questions, conditions = self._prepare_questions(request, db)

            # Process with Claude
            result = self._call_claude_api(document_content, questions, conditions)

            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)

            # Update session with results
            session.results = json.dumps(result)
            session.status = "completed"
            session.processing_time_ms = processing_time
            session.completed_at = datetime.now()
            db.commit()

            # Get processed file names
            files_processed = self._get_file_names(request.file_ids, db)

            return ChecklistResult(
                session_id=session_id,
                question_answers=result.get("question_answers", {}),
                condition_evaluations=result.get("condition_evaluations", {}),
                processing_time_ms=processing_time,
                files_processed=files_processed,
            )

        except Exception as e:
            # Update session with error
            processing_time = int((time.time() - start_time) * 1000)
            if "session" in locals():
                try:
                    db.rollback()  # Rollback any pending changes
                    session.status = "failed"
                    session.error_message = str(e)
                    session.processing_time_ms = processing_time
                    db.commit()
                except Exception:
                    db.rollback()  # If even the error update fails, rollback
            raise e

    def chat_with_documents(
        self, message: str, file_ids: List[int], db: Session
    ) -> Dict[str, str]:
        """
        Chat with Claude using documents as context.

        Args:
            message: User message
            file_ids: List of file IDs to use as context
            db: Database session

        Returns:
            Dict with response and files used
        """
        # Get document content
        document_content = self._extract_document_content(file_ids, db)

        # Prepare the full message with document context
        full_message = f"""Documents provided for context:
{document_content}

User question: {message}

Please answer the question based on the provided documents."""

        # Call Claude
        response = self.client.messages.create(
            model=settings.claude_model,
            max_tokens=settings.claude_max_tokens,
            messages=[{"role": "user", "content": full_message}],
        )

        # Get file names
        files_used = self._get_file_names(file_ids, db)

        return {"response": response.content[0].text, "files_used": files_used}

    def _extract_document_content(self, file_ids: List[int], db: Session) -> str:
        """Extract text content from specified files."""
        files = db.query(File).filter(File.id.in_(file_ids)).all()
        document_content = ""

        for file in files:
            pdf_text = self.file_service.extract_pdf_text(file.file_path)
            document_content += (
                f"\n\n--- Document: {file.original_filename} ---\n{pdf_text}\n"
            )

        return document_content

    def _prepare_questions(
        self, request: ChecklistRequest, db: Session
    ) -> tuple[List[str], List[str]]:
        """Prepare questions and conditions from request."""
        questions = []
        conditions = []

        # Add questions from IDs
        if request.question_ids:
            db_questions = (
                db.query(Question)
                .filter(
                    Question.id.in_(request.question_ids), Question.is_active == True
                )
                .all()
            )

            for q in db_questions:
                if q.type == "question":
                    questions.append(q.text)
                elif q.type == "condition":
                    conditions.append(q.text)

        # Add direct questions and conditions
        if request.questions:
            questions.extend(request.questions)
        if request.conditions:
            conditions.extend(request.conditions)

        return questions, conditions

    def _call_claude_api(
        self, document_content: str, questions: List[str], conditions: List[str]
    ) -> Dict:
        """Call Claude API with document content and questions."""
        system_prompt = """You are an expert document analyzer for German public tender documents. 
        Your task is to analyze the provided documents and answer questions or evaluate conditions.
        
        Ensure you thoroughly analyze all document content including text, quotes, tables, charts, and maintain the full context.

        For questions: Provide clear, specific answers based on the document content. If the information is not found, state "Information not found in documents".
        
        For conditions: Evaluate as true or false based on the document content. If you cannot determine the answer, respond with false and explain why.
        
        Always respond in valid JSON format with the following structure:
        {
            "question_answers": {"question_text": "answer"},
            "condition_evaluations": {"condition_text": <true/false> word only}
        }
        
        Be precise and cite specific sections of documents when possible."""

        # Combine all questions and conditions
        all_items = []

        if questions:
            all_items.extend([f"QUESTION: {q}" for q in questions])
        if conditions:
            all_items.extend([f"CONDITION: {c}" for c in conditions])

        if not all_items:
            return {"question_answers": {}, "condition_evaluations": {}}

        # Create the checklist processing message
        checklist_text = "\n".join(all_items)
        full_message = f"""Documents provided for analysis:
{document_content}

Please analyze the provided documents and process the following checklist items:

{checklist_text}

Respond in JSON format as specified in the system prompt."""

        # Call Claude
        response = self.client.messages.create(
            model=settings.claude_model,
            max_tokens=settings.claude_max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": full_message}],
        )

        # Parse the response
        try:
            result = json.loads(response.content[0].text)
            return result
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "question_answers": {"error": "Failed to parse response as JSON"},
                "condition_evaluations": {},
            }

    def _get_file_names(self, file_ids: List[int], db: Session) -> List[str]:
        """Get original filenames for given file IDs."""
        files = db.query(File).filter(File.id.in_(file_ids)).all()
        return [file.original_filename for file in files]
