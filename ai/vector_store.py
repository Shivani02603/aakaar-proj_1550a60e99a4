import os
from typing import List, Dict
from database.models import DocumentChunk
from database.config import SessionLocal

class VectorStore:
    def __init__(self):
        self.db_url = None

    def _get_db_url(self):
        if self.db_url is None:
            self.db_url = os.getenv("DATABASE_URL")
            if not self.db_url:
                raise ValueError("DATABASE_URL environment variable not set.")
        return self.db_url

    def upsert(self, id: str, vector: List[float], doc_metadata: Dict):
        if len(vector) != 1536:  # Ensure vector dimensionality matches spec
            raise ValueError(f"Vector dimensionality must be {1536}.")
        with SessionLocal() as session:
            chunk = session.query(DocumentChunk).filter_by(id=id).first()
            if chunk:
                chunk.embedding = vector
                chunk.doc_metadata = doc_metadata
            else:
                chunk = DocumentChunk(id=id, embedding=vector, doc_metadata=doc_metadata)
                session.add(chunk)
            session.commit()

    def search(self, query_embedding: List[float], top_k: int) -> List[Dict]:
        if len(query_embedding) != 1536:  # Ensure query embedding dimensionality matches spec
            raise ValueError(f"Query embedding dimensionality must be {1536}.")
        with SessionLocal() as session:
            results = (
                session.query(DocumentChunk)
                .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
                .limit(top_k)
                .all()
            )
            return [
                {"id": chunk.id, "content": chunk.content, "doc_metadata": chunk.doc_metadata}
                for chunk in results
            ]

# Singleton instance
vector_store = VectorStore()