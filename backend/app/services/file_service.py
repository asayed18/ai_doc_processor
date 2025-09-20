"""
File service for handling file uploads and text extraction.
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional

import PyPDF2
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.database import File
from ..schemas.schemas import FileCreate, FileResponse


class FileService:
    """Service for handling file operations."""

    def __init__(self):
        self.upload_dir = Path(settings.upload_directory)
        self.upload_dir.mkdir(exist_ok=True)

    async def upload_file(self, file: UploadFile, db: Session) -> FileResponse:
        """
        Upload a file and save it to storage.

        Args:
            file: The uploaded file
            db: Database session

        Returns:
            FileResponse with file information
        """
        # Validate file
        self._validate_file(file)

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        stored_filename = f"{file_id}{file_extension}"
        file_path = self.upload_dir / stored_filename

        # Save file
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to save file: {str(e)}"
            )

        # Create database record
        file_create = FileCreate(
            filename=stored_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=len(content),
            content_type=file.content_type,
        )

        db_file = File(**file_create.model_dump())
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        return FileResponse.model_validate(db_file)

    def get_files(self, db: Session) -> List[FileResponse]:
        """
        Get all uploaded files.

        Args:
            db: Database session

        Returns:
            List of file responses
        """
        files = db.query(File).order_by(File.upload_date.desc()).all()
        return [FileResponse.model_validate(file) for file in files]

    def get_file(self, file_id: int, db: Session) -> Optional[FileResponse]:
        """
        Get a specific file by ID.

        Args:
            file_id: The file ID
            db: Database session

        Returns:
            FileResponse or None if not found
        """
        file = db.query(File).filter(File.id == file_id).first()
        if file:
            return FileResponse.model_validate(file)
        return None

    def delete_file(self, file_id: int, db: Session) -> bool:
        """
        Delete a file from storage and database.

        Args:
            file_id: The file ID
            db: Database session

        Returns:
            True if deleted successfully
        """
        file = db.query(File).filter(File.id == file_id).first()
        if not file:
            return False

        # Delete physical file
        try:
            if os.path.exists(file.file_path):
                os.remove(file.file_path)
        except Exception:
            # Continue with database deletion even if file removal fails
            pass

        # Delete database record
        db.delete(file)
        db.commit()
        return True

    def extract_pdf_text(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content
        """
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    def _validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file.

        Args:
            file: The uploaded file

        Raises:
            HTTPException: If file is invalid
        """
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.allowed_file_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not allowed. Allowed types: {settings.allowed_file_types}",
            )

        # Check file size (if we can determine it)
        if hasattr(file.file, "seek") and hasattr(file.file, "tell"):
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(0)  # Reset to beginning

            if file_size > settings.max_file_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {settings.max_file_size} bytes",
                )
