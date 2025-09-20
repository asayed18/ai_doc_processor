import json
import os
import shutil
import sqlite3
import tempfile
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import anthropic
import PyPDF2

# Load environment variables
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="AI Document Processor", version="1.0.0")

# Get environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# CORS middleware for frontend communication
if IS_PRODUCTION:
    # Production: Restrict to specific domains
    allowed_origins = [
        "https://yourdomain.com",  # Replace with your production domain
        "https://www.yourdomain.com",
    ]
else:
    # Development: Allow all localhost variants
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*",  # Allow all origins in development
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# Database setup
def init_db():
    conn = sqlite3.connect("documents.db")
    cursor = conn.cursor()

    # Create files table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            anthropic_file_id TEXT NOT NULL,
            upload_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create questions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            type TEXT NOT NULL,  -- 'question' or 'condition'
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Insert default questions and conditions
    default_items = [
        (
            "In welcher Form sind die Angebote/Teilnahmeanträge einzureichen?",
            "question",
        ),
        ("Wann ist die Frist für die Einreichung von Bieterfragen?", "question"),
        ("Ist die Abgabefrist vor dem 31.12.2025?", "condition"),
    ]

    for text, item_type in default_items:
        cursor.execute("SELECT COUNT(*) FROM questions WHERE text = ?", (text,))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO questions (text, type) VALUES (?, ?)", (text, item_type)
            )

    conn.commit()
    conn.close()


# Initialize database on startup
init_db()


# Helper function to extract text from PDF
def extract_pdf_text(file_path: str) -> str:
    """Extract text content from a PDF file"""
    try:
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


# Pydantic models
class QuestionCreate(BaseModel):
    text: str
    type: str  # 'question' or 'condition'


class Question(BaseModel):
    id: int
    text: str
    type: str
    created_date: str


class FileInfo(BaseModel):
    id: int
    filename: str
    anthropic_file_id: str
    upload_date: str


class ChatRequest(BaseModel):
    message: str
    file_ids: List[int] = []
    questions: List[str] = []
    conditions: List[str] = []


class ChecklistResult(BaseModel):
    question_answers: Dict[str, str]
    condition_evaluations: Dict[str, bool]


@app.get("/")
async def root():
    return {"message": "AI Document Processor API"}


@app.get("/debug/cors")
async def debug_cors():
    """Debug endpoint to check CORS configuration"""
    return {
        "environment": ENVIRONMENT,
        "is_production": IS_PRODUCTION,
        "allowed_origins": allowed_origins
        if not IS_PRODUCTION
        else ["hidden for security"],
        "cors_enabled": True,
    }


@app.get("/debug")
async def debug_info():
    return {
        "message": "Debug Information",
        "environment": ENVIRONMENT,
        "is_production": IS_PRODUCTION,
        "allowed_cors_origins": allowed_origins
        if not IS_PRODUCTION
        else ["hidden in production"],
        "api_version": "1.0.0",
    }


@app.post("/upload", response_model=FileInfo)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and store it locally with a reference in database"""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        import uuid

        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        stored_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(upload_dir, stored_filename)

        # Save file locally
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Store in database
        conn = sqlite3.connect("documents.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO files (filename, anthropic_file_id) VALUES (?, ?)",
            (file.filename, file_path),  # Store local path instead of anthropic file id
        )
        file_id = cursor.lastrowid
        conn.commit()

        # Get the inserted record
        cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        conn.close()

        return FileInfo(
            id=row[0], filename=row[1], anthropic_file_id=row[2], upload_date=row[3]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/files", response_model=List[FileInfo])
async def get_files():
    """Get list of uploaded files"""
    try:
        conn = sqlite3.connect("documents.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files ORDER BY upload_date DESC")
        rows = cursor.fetchall()
        conn.close()

        return [
            FileInfo(
                id=row[0], filename=row[1], anthropic_file_id=row[2], upload_date=row[3]
            )
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch files: {str(e)}")


@app.post("/questions", response_model=Question)
async def create_question(question: QuestionCreate):
    """Create a new question or condition"""
    try:
        conn = sqlite3.connect("documents.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO questions (text, type) VALUES (?, ?)",
            (question.text, question.type),
        )
        question_id = cursor.lastrowid
        conn.commit()

        cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
        row = cursor.fetchone()
        conn.close()

        return Question(id=row[0], text=row[1], type=row[2], created_date=row[3])
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create question: {str(e)}"
        )


@app.get("/questions", response_model=List[Question])
async def get_questions():
    """Get all questions and conditions"""
    try:
        conn = sqlite3.connect("documents.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions ORDER BY created_date DESC")
        rows = cursor.fetchall()
        conn.close()

        return [
            Question(id=row[0], text=row[1], type=row[2], created_date=row[3])
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch questions: {str(e)}"
        )


@app.delete("/questions/{question_id}")
async def delete_question(question_id: int):
    """Delete a question or condition"""
    try:
        conn = sqlite3.connect("documents.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()
        conn.close()
        return {"message": "Question deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete question: {str(e)}"
        )


@app.post("/chat")
async def chat_with_claude(request: ChatRequest):
    """Chat with Claude using uploaded documents as context"""
    try:
        # Get file paths from database
        document_content = ""
        if request.file_ids:
            conn = sqlite3.connect("documents.db")
            cursor = conn.cursor()
            placeholders = ",".join("?" * len(request.file_ids))
            cursor.execute(
                f"SELECT filename, anthropic_file_id FROM files WHERE id IN ({placeholders})",
                request.file_ids,
            )
            files = cursor.fetchall()
            conn.close()

            # Extract text from PDFs
            for filename, file_path in files:
                pdf_text = extract_pdf_text(file_path)
                document_content += f"\n\n--- Document: {filename} ---\n{pdf_text}\n"

        # Prepare the full message with document context
        full_message = f"""Documents provided for context:
{document_content}

User question: {request.message}

Please answer the question based on the provided documents."""

        # Call Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": full_message}],
        )

        return {"response": response.content[0].text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.post("/checklist", response_model=ChecklistResult)
async def process_checklist(request: ChatRequest):
    """Process questions and conditions against uploaded documents"""
    try:
        # Get file paths from database and extract document content
        document_content = ""
        if request.file_ids:
            conn = sqlite3.connect("documents.db")
            cursor = conn.cursor()
            placeholders = ",".join("?" * len(request.file_ids))
            cursor.execute(
                f"SELECT filename, anthropic_file_id FROM files WHERE id IN ({placeholders})",
                request.file_ids,
            )
            files = cursor.fetchall()
            conn.close()

            # Extract text from PDFs
            for filename, file_path in files:
                pdf_text = extract_pdf_text(file_path)
                document_content += f"\n\n--- Document: {filename} ---\n{pdf_text}\n"

        # Prepare system prompt for checklist processing
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

        if request.questions:
            all_items.extend([f"QUESTION: {q}" for q in request.questions])
        if request.conditions:
            all_items.extend([f"CONDITION: {c}" for c in request.conditions])

        if not all_items:
            return ChecklistResult(question_answers={}, condition_evaluations={})

        # Create the checklist processing message
        checklist_text = "\n".join(all_items)
        full_message = f"""Documents provided for analysis:
{document_content}

Please analyze the provided documents and process the following checklist items:

{checklist_text}

Respond in JSON format as specified in the system prompt."""

        # Call Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": full_message}],
        )

        # Parse the response
        try:
            result = json.loads(response.content[0].text)
            print(result)
            return ChecklistResult(
                question_answers=result.get("question_answers", {}),
                condition_evaluations=result.get("condition_evaluations", {}),
            )
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return ChecklistResult(
                question_answers={"error": "Failed to parse response as JSON"},
                condition_evaluations={},
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Checklist processing failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
