from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import AsyncGenerator
from uuid import UUID
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime

from database.models import ChatMessage, ChatSession
from database.config import get_db

router = APIRouter(tags=["Streaming Responses"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class StreamQueryRequest(BaseModel):
    query_id: UUID = Field(..., description="Unique identifier for the query")


async def authenticate_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Simulated authentication logic
    user = db.query(ChatSession).filter(ChatSession.id == token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    return user


async def generate_streaming_response(query_id: UUID) -> AsyncGenerator[str, None]:
    # Simulated streaming logic
    for i in range(10):  # Simulate 10 tokens being streamed
        yield f"Token {i} for query {query_id}\n"
        await asyncio.sleep(0.5)  # Simulate delay between tokens


@router.get("/stream/query/{query_id}", response_class=StreamingResponse)
async def stream_query_response(
    query_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    user: ChatSession = Depends(authenticate_user),
):
    """
    Stream the answer tokens for a given query in real-time.
    """
    # Validate query ID
    query = db.query(ChatMessage).filter(ChatMessage.id == query_id).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query not found")

    # Stream response
    return StreamingResponse(
        generate_streaming_response(query_id),
        media_type="text/plain",
    )