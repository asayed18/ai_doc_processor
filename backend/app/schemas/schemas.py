"""
Pydantic schemas for API requests and responses.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# File schemas
class FileBase(BaseModel):
    """Base file schema."""

    filename: str
    original_filename: str


class FileCreate(FileBase):
    """Schema for creating a file."""

    file_path: str
    file_size: int
    content_type: Optional[str] = None


class FileResponse(FileBase):
    """Schema for file responses."""

    id: int
    file_size: int
    content_type: Optional[str]
    upload_date: datetime
    anthropic_file_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Question schemas
class QuestionBase(BaseModel):
    """Base question schema."""

    text: str = Field(..., min_length=1, max_length=50000)
    type: str = Field(..., pattern="^(question|condition)$")


class QuestionCreate(QuestionBase):
    """Schema for creating a question."""

    pass


class QuestionUpdate(BaseModel):
    """Schema for updating a question."""

    text: Optional[str] = Field(None, min_length=1, max_length=1000)
    type: Optional[str] = Field(None, pattern="^(question|condition)$")
    is_active: Optional[bool] = None


class QuestionResponse(QuestionBase):
    """Schema for question responses."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Processing schemas
class ChecklistRequest(BaseModel):
    """Schema for checklist processing requests."""

    file_ids: List[int] = Field(default_factory=list)
    question_ids: Optional[List[int]] = None
    questions: Optional[List[str]] = None
    conditions: Optional[List[str]] = None


class ChecklistResult(BaseModel):
    """Schema for checklist processing results."""

    session_id: str
    question_answers: Dict[str, str]
    condition_evaluations: Dict[str, bool]
    processing_time_ms: int
    files_processed: List[str]


class ProcessingSessionResponse(BaseModel):
    """Schema for processing session responses."""

    id: int
    session_id: str
    status: str
    file_ids: List[int]
    question_ids: List[int]
    results: Optional[Dict] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Chat schemas
class ChatRequest(BaseModel):
    """Schema for chat requests."""

    message: str = Field(..., max_length=50000)
    file_ids: List[int] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Schema for chat responses."""

    response: str
    files_used: List[str]


# API Response schemas
class APIResponse(BaseModel):
    """Generic API response schema."""

    success: bool
    message: str
    data: Optional[Dict] = None


class ErrorResponse(BaseModel):
    """Error response schema."""

    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
