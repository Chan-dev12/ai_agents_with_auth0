# import uuid
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
# from langchain_postgres import PGVectorStore, PGEngine
# from pydantic import SecretStr

# from app.core.config import settings
# from app.core.db import engine
# from app.models.embeddings import Embedding

# from langchain_ollama import OllamaEmbeddings

# embedding_model = OllamaEmbeddings(
#     model="nomic-embed-text",   # or whatever embedding model you pulled in Ollama
#     base_url=settings.OLLAMA_BASE_URL,  # e.g. "http://localhost:11434"
# )

# vector_store: PGVectorStore | None = None


# def generate_embeddings(
#     document_id: uuid.UUID, file_name: str, text: str
# ) -> list[Embedding]:
#     """Generate embeddings for a document."""
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=100,
#         chunk_overlap=10,
#         length_function=len,
#     )

#     # chunks = splitter.create_documents([text])
#     # embeddings = embedding_model.embed_documents(
#     #     [chunk.page_content for chunk in chunks]
#     # )

#     # return [
#     #     Embedding(
#     #         document_id=document_id,
#     #         meta={
#     #             "file_name": file_name,
#     #             "document_id": str(document_id),
#     #         },
#     #         content=chunk.page_content,
#     #         embedding=embedding,
#     #     )
#     #     # for chunk, embedding in zip(chunks, embeddings)
#     # ]


# async def get_vector_store():
#     global vector_store

#     if vector_store is not None:
#         return vector_store

#     pg_engine = PGEngine.from_connection_string(settings.DATABASE_URL)
#     vector_store = await PGVectorStore.create(
#         engine=pg_engine,
#         table_name="embedding",
#         # embedding_service=embedding_model,
#         id_column="id",
#         embedding_column="embedding",
#         content_column="content",
#         metadata_json_column="meta",
#     )

#     return vector_store
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres import PGVectorStore, PGEngine
from sqlmodel import Session, select, col

from app.core.config import settings
from app.core.db import engine
from app.models.embeddings import Embedding
from app.models.documents import Document

from langchain_ollama import OllamaEmbeddings

embedding_model = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=settings.OLLAMA_BASE_URL,
)

vector_store: PGVectorStore | None = None


def generate_embeddings(
    document_id: uuid.UUID, file_name: str, text: str
) -> list[Embedding]:
    """Generate embeddings for a document."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )

    chunks = splitter.create_documents([text])
    if not chunks:
        return []

    embeddings = embedding_model.embed_documents(
        [chunk.page_content for chunk in chunks]
    )

    return [
        Embedding(
            document_id=document_id,
            meta={
                "file_name": file_name,
                "document_id": str(document_id),
            },
            content=chunk.page_content,
            embedding=embedding,
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]


async def get_vector_store():
    global vector_store

    if vector_store is not None:
        return vector_store

    pg_engine = PGEngine.from_connection_string(settings.DATABASE_URL)
    vector_store = await PGVectorStore.create(
        engine=pg_engine,
        table_name="embedding",
        embedding_service=embedding_model,
        id_column="id",
        embedding_column="embedding",
        content_column="content",
        metadata_json_column="meta",
    )

    return vector_store


def get_accessible_document_ids(user_email: str, user_sub: str) -> list[str]:
    """
    SECURITY BOUNDARY: returns only document IDs this user is allowed to see —
    documents they own, or documents explicitly shared with their email.
    This list is used to filter retrieval BEFORE any content reaches the LLM.
    """
    with Session(engine) as db_session:
        documents = db_session.exec(
            select(Document.id, Document.user_id, Document.shared_with)
        ).all()

        accessible_ids = [
            str(doc.id)
            for doc in documents
            if doc.user_id == user_sub or (doc.shared_with and user_email in doc.shared_with)
        ]
        return accessible_ids


async def search_documents(
    query: str, user_email: str, user_sub: str, k: int = 4
) -> list[dict]:
    """
    Retrieve relevant document chunks for a query, filtered to ONLY documents
    this specific user is authorized to access (owned or shared-with).
    """
    accessible_ids = get_accessible_document_ids(user_email, user_sub)
    if not accessible_ids:
        return []

    store = await get_vector_store()

    results = await store.asimilarity_search(
        query,
        k=k,
        filter={"document_id": {"$in": accessible_ids}},
    )

    return [
        {
            "content": doc.page_content,
            "file_name": doc.metadata.get("file_name", "unknown"),
        }
        for doc in results
    ]