import uuid
from typing import List, Optional

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models import DocumentChunk
from database.config import get_db


class VectorStorageService:
    def __init__(self, db: Session):
        self.db = db

    def create_document_chunk(
        self, document_id: uuid.UUID, chunk_index: int, content: str, embedding: List[float], metadata: dict
    ) -> DocumentChunk:
        try:
            new_chunk = DocumentChunk(
                id=uuid.uuid4(),
                document_id=document_id,
                chunk_index=chunk_index,
                content=content,
                embedding=embedding,
                metadata=metadata,
                created_at=datetime.utcnow(),
            )
            self.db.add(new_chunk)
            self.db.commit()
            self.db.refresh(new_chunk)
            return new_chunk
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create document chunk: {str(e)}")

    def get_document_chunk_by_id(self, chunk_id: uuid.UUID) -> DocumentChunk:
        chunk = self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Document chunk not found")
        return chunk

    def list_all_document_chunks(self, document_id: uuid.UUID) -> List[DocumentChunk]:
        try:
            chunks = self.db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
            return chunks
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Failed to list document chunks: {str(e)}")

    def update_document_chunk(
        self, chunk_id: uuid.UUID, content: Optional[str] = None, embedding: Optional[List[float]] = None, metadata: Optional[dict] = None
    ) -> DocumentChunk:
        chunk = self.get_document_chunk_by_id(chunk_id)
        try:
            if content is not None:
                chunk.content = content
            if embedding is not None:
                chunk.embedding = embedding
            if metadata is not None:
                chunk.metadata = metadata
            chunk.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(chunk)
            return chunk
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update document chunk: {str(e)}")

    def delete_document_chunk(self, chunk_id: uuid.UUID) -> None:
        chunk = self.get_document_chunk_by_id(chunk_id)
        try:
            self.db.delete(chunk)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete document chunk: {str(e)}")