import os
from typing import List
import openai

# Constants
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

class EmbeddingClient:
    def __init__(self):
        self.api_key = None

    def _get_client(self):
        if self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set.")
        return openai.OpenAI(api_key=self.api_key)

    def embed_text(self, text: str) -> List[float]:
        client = self._get_client()
        response = client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
        if len(response.data) != 1:
            raise ValueError("Unexpected response length from embedding API.")
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        client = self._get_client()
        response = client.embeddings.create(input=texts, model=EMBEDDING_MODEL)
        if len(response.data) != len(texts):
            raise ValueError("Mismatch between input texts and response embeddings.")
        return [item.embedding for item in response.data]

# Module-level function for embedding
def get_embedding(texts: List[str]) -> List[List[float]]:
    client = EmbeddingClient()
    return client.embed_batch(texts)