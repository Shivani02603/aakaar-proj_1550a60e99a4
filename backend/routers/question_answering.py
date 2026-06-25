from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer

from database.models import DocumentChunk
from database.config import get_db
from backend.services.question_answering_service import generate_answer_with_citations

router = APIRouter(tags=["Question Answering"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Pydantic schemas
class QueryRequest(BaseModel):
    query: str = Field(..., example="What is the capital of France?")


class Citation(BaseModel):
    chunk_id: UUID
    content: str
    metadata: dict


class AnswerResponse(BaseModel):
    answer: str
    citations: List[Citation]


# Dependency for authentication
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Placeholder for actual user authentication logic
    # Replace with actual JWT decoding and user validation
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return {"user_id": "example_user_id"}  # Replace with actual user data


@router.post("/question-answer", response_model=AnswerResponse)
async def question_answer(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Endpoint to accept a user query, retrieve relevant chunks, and generate an answer with citations.
    """
    try:
        # Generate answer and retrieve citations using the service layer
        answer, citations = generate_answer_with_citations(request.query, db)

        # Format citations for response
        formatted_citations = [
            Citation(
                chunk_id=citation["chunk_id"],
                content=citation["content"],
                metadata=citation["metadata"],
            )
            for citation in citations
        ]

        return AnswerResponse(answer=answer, citations=formatted_citations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the query.",
        )