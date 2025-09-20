"""
Database models for the AI Document Processor application.
"""


from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class File(Base):
    """File model for uploaded documents."""

    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100))
    md5_hash = Column(
        String(32), nullable=True, index=True
    )  # MD5 hash for deduplication
    anthropic_file_id = Column(
        String(255), nullable=True
    )  # For future Anthropic Files API integration
    upload_date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<File(id={self.id}, filename='{self.filename}')>"


class Question(Base):
    """Question model for storing user questions and conditions."""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    type = Column(String(50), nullable=False, index=True)  # 'question' or 'condition'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<Question(id={self.id}, type='{self.type}', text='{self.text[:50]}...')>"
        )


class ProcessingSession(Base):
    """Model for tracking document processing sessions."""

    __tablename__ = "processing_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    file_ids = Column(Text)  # JSON array of file IDs
    question_ids = Column(Text)  # JSON array of question IDs
    results = Column(Text)  # JSON results from Claude
    status = Column(
        String(50), default="pending", nullable=False
    )  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<ProcessingSession(id={self.id}, session_id='{self.session_id}', status='{self.status}')>"
