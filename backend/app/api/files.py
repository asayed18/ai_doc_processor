"""
File management API routes.
"""

from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..schemas.schemas import FileResponse
from ..services.file_service import FileService

router = APIRouter(prefix="/files", tags=["files"])
file_service = FileService()


@router.post("/upload", response_model=FileResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a new file."""
    return await file_service.upload_file(file, db)


@router.get("/", response_model=List[FileResponse])
def get_files(db: Session = Depends(get_db)):
    """Get all uploaded files."""
    return file_service.get_files(db)


@router.get("/{file_id}", response_model=FileResponse)
def get_file(file_id: int, db: Session = Depends(get_db)):
    """Get a specific file by ID."""
    file = file_service.get_file(file_id, db)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file


@router.delete("/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    """Delete a file."""
    success = file_service.delete_file(file_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted successfully"}
