from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import List

from database.models import Document, DocumentChunk
from database.config import get_db
from backend.services.document_processing_service import process_document_chunks
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["Document Processing"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


# Pydantic schemas
class DocumentBase(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    file_size: int
    status: str
    uploaded_at: datetime
    processed_at: datetime | None


class DocumentResponse(DocumentBase):
    pass


class DocumentChunkBase(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    embedding: List[float]
    metadata: dict
    created_at: datetime


class DocumentChunkResponse(DocumentChunkBase):
    pass


# Dependency for JWT authentication
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user


@router.post("/documents/{document_id}/process", response_model=DocumentResponse)
async def process_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Process a document by extracting text, splitting into chunks, and generating embeddings.
    """
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status != "uploaded":
        raise HTTPException(status_code=400, detail="Document is not in a valid state for processing")

    # Update document status to processing
    document.status = "processing"
    db.commit()

    # Add background task for processing
    background_tasks.add_task(process_document_chunks, document_id, db)

    return DocumentResponse.from_orm(document)


@router.get("/documents/{document_id}/chunks", response_model=List[DocumentChunkResponse])
async def get_document_chunks(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all chunks for a specific document.
    """
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
    return [DocumentChunkResponse.from_orm(chunk) for chunk in chunks]


@router.get("/documents/{document_id}/chunks/{chunk_id}", response_model=DocumentChunkResponse)
async def get_document_chunk(
    document_id: UUID,
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific chunk for a document.
    """
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id, DocumentChunk.document_id == document_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Document chunk not found")

    return DocumentChunkResponse.from_orm(chunk)


@router.delete("/documents/{document_id}/chunks/{chunk_id}", response_model=dict)
async def delete_document_chunk(
    document_id: UUID,
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a specific chunk for a document.
    """
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id, DocumentChunk.document_id == document_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Document chunk not found")

    db.delete(chunk)
    db.commit()

    return {"detail": "Document chunk deleted successfully"}