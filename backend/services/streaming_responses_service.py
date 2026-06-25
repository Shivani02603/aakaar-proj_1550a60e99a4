import uuid
from typing import List, Optional

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models import ChatMessage
from database.config import get_db


class StreamingResponsesService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_streaming_response(self, session_id: uuid.UUID, role: str, content: str, citations: Optional[dict] = None) -> ChatMessage:
        try:
            new_message = ChatMessage(
                id=uuid.uuid4(),
                session_id=session_id,
                role=role,
                content=content,
                citations=citations or {},
                created_at=datetime.utcnow()
            )
            self.db.add(new_message)
            self.db.commit()
            self.db.refresh(new_message)
            return new_message
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create streaming response.") from e

    def get_streaming_response_by_id(self, message_id: uuid.UUID) -> ChatMessage:
        try:
            message = self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            if not message:
                raise HTTPException(status_code=404, detail="Streaming response not found.")
            return message
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Failed to retrieve streaming response.") from e

    def list_all_streaming_responses(self, session_id: uuid.UUID) -> List[ChatMessage]:
        try:
            messages = self.db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
            return messages
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Failed to list streaming responses.") from e

    def update_streaming_response(self, message_id: uuid.UUID, content: Optional[str] = None, citations: Optional[dict] = None) -> ChatMessage:
        try:
            message = self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            if not message:
                raise HTTPException(status_code=404, detail="Streaming response not found.")
            
            if content is not None:
                message.content = content
            if citations is not None:
                message.citations = citations
            
            self.db.commit()
            self.db.refresh(message)
            return message
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update streaming response.") from e

    def delete_streaming_response(self, message_id: uuid.UUID) -> None:
        try:
            message = self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            if not message:
                raise HTTPException(status_code=404, detail="Streaming response not found.")
            
            self.db.delete(message)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete streaming response.") from e