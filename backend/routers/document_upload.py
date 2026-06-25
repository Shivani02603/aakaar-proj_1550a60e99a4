from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
import os

from database.models import Document, User
from database.config import get_db
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["Document Upload"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


# Pydantic Schemas
class DocumentBase(BaseModel):
    filename: str
    file_size: int
    status: str
    uploaded_at: datetime
    processed_at: datetime | None = None


class DocumentResponse(DocumentBase):
    id: UUID
    user_id: UUID


class DocumentCreate(BaseModel):
    filename: str = Field(..., example="example.pdf")
    file_size: int = Field(..., example=1024)
    status: str = Field(..., example="uploaded")


# Utility function to get the current user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.id == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user


# Routes
@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a document for processing.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_size = len(await file.read())
    file.seek(0)  # Reset file pointer after reading

    # Save file to server (optional, adjust path as needed)
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Create document record in the database
    new_document = Document(
        id=UUID(),
        user_id=current_user.id,
        filename=file.filename,
        file_size=file_size,
        status="uploaded",
        uploaded_at=datetime.utcnow(),
    )
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document


@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all documents uploaded by the current user.
    """
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get details of a specific document.
    """
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/documents/{document_id}", response_model=dict)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a specific document.
    """
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(document)
    db.commit()

    # Optionally delete the file from the server
    upload_dir = "uploads"
    file_path = os.path.join(upload_dir, document.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    return {"detail": "Document deleted successfully"}