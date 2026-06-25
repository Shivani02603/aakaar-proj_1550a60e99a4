from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from database.models import DocumentChunk
from database.config import get_db
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer

# OAuth2 dependency for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# APIRouter setup
router = APIRouter(tags=["Vector Storage"])


# Pydantic schemas
class DocumentChunkBase(BaseModel):
    document_id: UUID
    chunk_index: int
    content: str
    embedding: List[float]
    metadata: dict


class DocumentChunkCreate(DocumentChunkBase):
    pass


class DocumentChunkUpdate(BaseModel):
    content: str | None = None
    embedding: List[float] | None = None
    metadata: dict | None = None


class DocumentChunkResponse(DocumentChunkBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


# Dependency for JWT authentication
def get_current_user(token: str = Depends(oauth2_scheme)) -> UUID:
    # Simulated user extraction from token (replace with actual implementation)
    user_id = UUID("12345678-1234-5678-1234-567812345678")  # Example user ID
    return user_id


# Routes
@router.get("/vector-storage", response_model=List[DocumentChunkResponse])
def list_document_chunks(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    chunks = db.query(DocumentChunk).filter(DocumentChunk.metadata["user_id"].astext == str(user_id)).all()
    return chunks


@router.get("/vector-storage/{chunk_id}", response_model=DocumentChunkResponse)
def get_document_chunk(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
    if not chunk or chunk.metadata.get("user_id") != str(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document chunk not found")
    return chunk


@router.post("/vector-storage", response_model=DocumentChunkResponse, status_code=status.HTTP_201_CREATED)
def create_document_chunk(
    chunk: DocumentChunkCreate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    new_chunk = DocumentChunk(
        id=UUID(),
        document_id=chunk.document_id,
        chunk_index=chunk.chunk_index,
        content=chunk.content,
        embedding=chunk.embedding,
        metadata={**chunk.metadata, "user_id": str(user_id)},
        created_at=datetime.utcnow(),
    )
    db.add(new_chunk)
    db.commit()
    db.refresh(new_chunk)
    return new_chunk


@router.put("/vector-storage/{chunk_id}", response_model=DocumentChunkResponse)
def update_document_chunk(
    chunk_id: UUID,
    chunk_update: DocumentChunkUpdate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
    if not chunk or chunk.metadata.get("user_id") != str(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document chunk not found")

    if chunk_update.content is not None:
        chunk.content = chunk_update.content
    if chunk_update.embedding is not None:
        chunk.embedding = chunk_update.embedding
    if chunk_update.metadata is not None:
        chunk.metadata.update(chunk_update.metadata)

    chunk.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(chunk)
    return chunk


@router.delete("/vector-storage/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_chunk(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
    if not chunk or chunk.metadata.get("user_id") != str(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document chunk not found")

    db.delete(chunk)
    db.commit()