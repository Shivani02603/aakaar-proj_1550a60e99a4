import os
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from sse_starlette.sse import EventSourceResponse
from typing import AsyncGenerator

# Initialize FastAPI app
app = FastAPI()

# Environment variables for API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PGVECTOR_DB_URL = os.getenv("PGVECTOR_DB_URL")

# Initialize embedding model and vector store
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY)
vector_store = PGVector(embedding_model=embedding_model, connection_string=PGVECTOR_DB_URL)

# Initialize LLM
llm = OpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY, streaming=True)

async def stream_answer(query: str, session_id: str, user_id: str) -> AsyncGenerator[str, None]:
    # Step 1: Embed query
    query_embedding = embedding_model.embed_query(query)

    # Step 2: Retrieve top-5 chunks from vector store
    top_chunks = vector_store.search(query_embedding, top_k=5)

    # Step 3: Build prompt with retrieved context
    context = "\n\n".join([chunk["text"] for chunk in top_chunks])
    citations = [chunk["source"] for chunk in top_chunks]
    prompt_template = PromptTemplate(
        template="Answer the following question based on the context provided:\n\nContext:\n{context}\n\nQuestion:\n{query}",
        input_variables=["context", "query"]
    )
    prompt = prompt_template.format(context=context, query=query)

    # Step 4: Call gpt-4o with stream=True
    async for token in llm.stream(prompt):
        yield f'data: {{"token": "{token}"}}\n'

    # Step 6: After final token, yield done signal with citations
    yield f'data: {{"done": true, "citations": {citations}}}\n'

@app.get("/stream")
async def stream(query: str = Query(...), session_id: str = Query(...), user_id: str = Query(...)):
    return EventSourceResponse(stream_answer(query, session_id, user_id))