import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.models import Document, DocumentChunk
from database.config import get_db
from openai import OpenAI

class DocumentProcessingService:
    def __init__(self, db: Session):
        self.db = db

    def create_document_chunk(self, document_id: uuid.UUID, chunk_index: int, content: str, embedding: List[float], metadata: dict) -> DocumentChunk:
        """Create a new document chunk."""
        document_chunk = DocumentChunk(
            id=uuid.uuid4(),
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            embedding=embedding,
            metadata=metadata,
            created_at=datetime.utcnow()
        )
        self.db.add(document_chunk)
        self.db.commit()
        self.db.refresh(document_chunk)
        return document_chunk

    def get_document_by_id(self, document_id: uuid.UUID) -> Document:
        """Retrieve a document by its ID."""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    def list_all_documents(self) -> List[Document]:
        """List all documents."""
        return self.db.query(Document).all()

    def update_document_status(self, document_id: uuid.UUID, status: str) -> Document:
        """Update the status of a document."""
        document = self.get_document_by_id(document_id)
        document.status = status
        document.processed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete_document(self, document_id: uuid.UUID) -> None:
        """Delete a document."""
        document = self.get_document_by_id(document_id)
        self.db.delete(document)
        self.db.commit()

    def process_document(self, document_id: uuid.UUID) -> List[DocumentChunk]:
        """
        Process a document by extracting text, splitting into chunks, and generating embeddings.
        """
        document = self.get_document_by_id(document_id)

        # Simulate text extraction from the document (replace with actual PDF text extraction logic)
        extracted_text = self._extract_text_from_pdf(document.filename)

        # Split text into chunks
        chunks = self._split_text_into_chunks(extracted_text, chunk_size=1000, overlap=200)

        # Generate embeddings for each chunk
        document_chunks = []
        for index, chunk in enumerate(chunks):
            embedding = self._generate_embedding(chunk)
            metadata = {"chunk_index": index, "source_document": document.filename}
            document_chunk = self.create_document_chunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding=embedding,
                metadata=metadata
            )
            document_chunks.append(document_chunk)

        # Update document status
        self.update_document_status(document_id, status="processed")
        return document_chunks

    def _extract_text_from_pdf(self, filename: str) -> str:
        """
        Extract text from a PDF file.
        Replace this stub with actual PDF text extraction logic.
        """
        # Placeholder for PDF text extraction logic
        return "Extracted text from the PDF file."

    def _split_text_into_chunks(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        Split text into overlapping chunks.
        """
        tokens = text.split()
        chunks = []
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk = tokens[i:i + chunk_size]
            chunks.append(" ".join(chunk))
        return chunks

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings using OpenAI's text-embedding-3-small model.
        Replace this stub with actual embedding generation logic.
        """
        # Simulate embedding generation (replace with actual OpenAI API call)
        openai_client = OpenAI(api_key="your_openai_api_key")
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response["data"][0]["embedding"]