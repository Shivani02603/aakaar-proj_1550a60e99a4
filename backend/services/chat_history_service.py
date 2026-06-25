import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models import ChatSession, ChatMessage
from database.config import get_db


class ChatHistoryService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_chat_session(self, user_id: uuid.UUID, title: str) -> ChatSession:
        try:
            new_session = ChatSession(
                id=uuid.uuid4(),
                user_id=user_id,
                title=title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self.db.add(new_session)
            self.db.commit()
            self.db.refresh(new_session)
            return new_session
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create chat session") from e

    def get_chat_session_by_id(self, session_id: uuid.UUID) -> ChatSession:
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return session

    def list_chat_sessions(self, user_id: uuid.UUID) -> List[ChatSession]:
        try:
            sessions = self.db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
            return sessions
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Failed to retrieve chat sessions") from e

    def update_chat_session(self, session_id: uuid.UUID, title: Optional[str]) -> ChatSession:
        try:
            session = self.get_chat_session_by_id(session_id)
            if title:
                session.title = title
                session.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(session)
            return session
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update chat session") from e

    def delete_chat_session(self, session_id: uuid.UUID) -> None:
        try:
            session = self.get_chat_session_by_id(session_id)
            self.db.delete(session)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete chat session") from e

    def create_chat_message(
        self, session_id: uuid.UUID, role: str, content: str, citations: Optional[dict] = None
    ) -> ChatMessage:
        try:
            new_message = ChatMessage(
                id=uuid.uuid4(),
                session_id=session_id,
                role=role,
                content=content,
                citations=citations or {},
                created_at=datetime.utcnow(),
            )
            self.db.add(new_message)
            self.db.commit()
            self.db.refresh(new_message)
            return new_message
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create chat message") from e

    def get_chat_messages_by_session_id(self, session_id: uuid.UUID) -> List[ChatMessage]:
        try:
            messages = self.db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
            if not messages:
                raise HTTPException(status_code=404, detail="No messages found for this session")
            return messages
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Failed to retrieve chat messages") from e

    def delete_chat_message(self, message_id: uuid.UUID) -> None:
        try:
            message = self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
            if not message:
                raise HTTPException(status_code=404, detail="Chat message not found")
            self.db.delete(message)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete chat message") from e