"""
Claude File API service for managing file uploads and references.

This service handles Claude's Files API operations:
- File uploads to Claude's storage with proper beta headers
- Document content block creation for message references
- File cleanup and deletion from Claude's storage
- File listing and management

Uses the beta Files API (anthropic-beta: files-api-2025-04-14)
For more information: https://docs.claude.com/en/docs/build-with-claude/files
"""

from pathlib import Path
from typing import Dict, List

import anthropic
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.database import File


class ClaudeFileService:
    """Service for managing Claude File API operations."""

    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=settings.anthropic_api_key,
            # Add beta header for Files API
            default_headers={"anthropic-beta": "files-api-2025-04-14"},
        )

    def get_file_references(self, file_ids: List[int], db: Session) -> List[Dict]:
        """
        Get Claude file references for uploaded files.

        Args:
            file_ids: List of local file IDs
            db: Database session

        Returns:
            List of document content blocks for Claude messages
        """
        files = db.query(File).filter(File.id.in_(file_ids)).all()
        file_references = []

        for file in files:
            if not file.anthropic_file_id:
                # Upload file to Claude if not already uploaded
                try:
                    claude_file = self.client.beta.files.upload(
                        file=Path(file.file_path)
                    )

                    # Store the Claude file ID
                    file.anthropic_file_id = claude_file.id
                    db.commit()

                    # Add document reference
                    file_references.append(
                        {
                            "type": "document",
                            "source": {"type": "file", "file_id": claude_file.id},
                            "title": file.original_filename,
                        }
                    )

                except Exception as e:
                    print(
                        f"Failed to upload file {file.original_filename} to Claude: {e}"
                    )
                    # Fallback: use text content instead
                    try:
                        # Import here to avoid circular imports
                        from .file_service import FileService

                        file_service = FileService()
                        text_content = file_service.extract_pdf_text(file.file_path)
                        file_references.append(
                            {
                                "type": "text",
                                "text": f"[Document: {file.original_filename}]\n{text_content}",
                            }
                        )
                    except Exception as text_error:
                        print(
                            f"Failed to extract text from {file.original_filename}: {text_error}"
                        )
                    continue
            else:
                # Use existing Claude file reference
                file_references.append(
                    {
                        "type": "document",
                        "source": {"type": "file", "file_id": file.anthropic_file_id},
                        "title": file.original_filename,
                    }
                )

        return file_references

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Claude's storage.

        Args:
            file_id: Claude file ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.beta.files.delete(file_id)
            return True
        except Exception as e:
            print(f"Failed to delete Claude file {file_id}: {e}")
            return False

    def list_files(self) -> List[Dict]:
        """
        List all files in Claude's storage.

        Returns:
            List of file information dictionaries
        """
        try:
            response = self.client.beta.files.list()
            return response.data if hasattr(response, "data") else []
        except Exception as e:
            print(f"Failed to list Claude files: {e}")
            return []

    def upload_file(self, file_path: str, purpose: str = "user_data") -> str:
        """
        Upload a file to Claude's storage.

        Args:
            file_path: Path to the file to upload
            purpose: Purpose of the file upload

        Returns:
            Claude file ID if successful, None otherwise
        """
        try:
            claude_file = self.client.beta.files.upload(
                file=Path(file_path), purpose=purpose
            )
            return claude_file.id
        except Exception as e:
            print(f"Failed to upload file {file_path} to Claude: {e}")
            return None

    def get_file_info(self, file_id: str) -> Dict:
        """
        Get information about a file in Claude's storage.

        Args:
            file_id: Claude file ID

        Returns:
            File information dictionary
        """
        try:
            response = self.client.beta.files.retrieve_metadata(file_id)
            return response.__dict__ if hasattr(response, "__dict__") else {}
        except Exception as e:
            print(f"Failed to get info for Claude file {file_id}: {e}")
            return {}
