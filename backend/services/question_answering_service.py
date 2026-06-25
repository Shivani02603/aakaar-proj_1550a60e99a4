import uuid
from typing import List, Dict, Optional
from datetime import datetime

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models import DocumentChunk
from database.config import get_db
from openai import OpenAI

class QuestionAnsweringService:
    def __init__(self, db: Session):
        self.db = db

    def create_chunk(self, document_id: uuid.UUID, chunk_index: int, content: str, embedding: List[float], metadata: Dict) -> DocumentChunk:
        try:
            new_chunk = DocumentChunk(
                id=uuid.uuid4(),
                document_id=document_id,
                chunk_index=chunk_index,
                content=content,
                embedding=embedding,
                metadata=metadata,
                created_at=datetime.utcnow()
            )
            self.db.add(new_chunk)
            self.db.commit()
            self.db.refresh(new_chunk)
            return new_chunk
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating chunk: {str(e)}")

    def get_chunk_by_id(self, chunk_id: uuid.UUID) -> DocumentChunk:
        chunk = self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        return chunk

    def list_all_chunks(self, document_id: uuid.UUID) -> List[DocumentChunk]:
        chunks = self.db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
        if not chunks:
            raise HTTPException(status_code=404, detail="No chunks found for the given document")
        return chunks

    def update_chunk(self, chunk_id: uuid.UUID, content: Optional[str] = None, metadata: Optional[Dict] = None) -> DocumentChunk:
        chunk = self.get_chunk_by_id(chunk_id)
        if content:
            chunk.content = content
        if metadata:
            chunk.metadata = metadata
        chunk.updated_at = datetime.utcnow()
        try:
            self.db.commit()
            self.db.refresh(chunk)
            return chunk
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating chunk: {str(e)}")

    def delete_chunk(self, chunk_id: uuid.UUID) -> None:
        chunk = self.get_chunk_by_id(chunk_id)
        try:
            self.db.delete(chunk)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting chunk: {str(e)}")

    def answer_question(self, query: str) -> Dict:
        """
        Accepts a user query, retrieves the top-5 most relevant chunks, and generates a concise answer
        using a large language model with citations to the source chunks.
        """
        try:
            # Retrieve top-5 relevant chunks based on embeddings (mock implementation)
            chunks = self.db.query(DocumentChunk).order_by(DocumentChunk.chunk_index).limit(5).all()
            if not chunks:
                raise HTTPException(status_code=404, detail="No relevant chunks found")

            # Prepare context for the LLM
            context = "\n".join([chunk.content for chunk in chunks])
            citations = [{"chunk_id": str(chunk.id), "metadata": chunk.metadata} for chunk in chunks]

            # Generate answer using LLM (mock implementation)
            llm = OpenAI()  # Replace with actual LLM client initialization
            response = llm.generate_answer(prompt=f"Context: {context}\n\nQuestion: {query}")

            return {
                "answer": response,
                "citations": citations
            }
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving chunks: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")