import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.models import Document, User
from database.config import get_db


class DocumentUploadService:
    def __init__(self, db: Session):
        self.db = db

    def create_document(self, user_id: uuid.UUID, filename: str, file_size: int, status: str = "uploaded") -> Document:
        """
        Create a new document entry in the database.
        """
        new_document = Document(
            id=uuid.uuid4(),
            user_id=user_id,
            filename=filename,
            file_size=file_size,
            status=status,
            uploaded_at=datetime.utcnow(),
            processed_at=None,
        )
        self.db.add(new_document)
        self.db.commit()
        self.db.refresh(new_document)
        return new_document

    def get_document_by_id(self, document_id: uuid.UUID) -> Document:
        """
        Retrieve a document by its ID.
        """
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    def list_documents(self, user_id: uuid.UUID) -> List[Document]:
        """
        List all documents for a specific user.
        """
        documents = self.db.query(Document).filter(Document.user_id == user_id).all()
        return documents

    def update_document_status(self, document_id: uuid.UUID, status: str) -> Document:
        """
        Update the status of a document.
        """
        document = self.get_document_by_id(document_id)
        document.status = status
        document.processed_at = datetime.utcnow() if status == "processed" else None
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete_document(self, document_id: uuid.UUID) -> None:
        """
        Delete a document by its ID.
        """
        document = self.get_document_by_id(document_id)
        self.db.delete(document)
        self.db.commit()


# Dependency function to use the service
def get_document_upload_service(db: Session = Depends(get_db)) -> DocumentUploadService:
    return DocumentUploadService(db)