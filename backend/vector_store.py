import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from backend.config import settings

if settings.qdrant_url.startswith("http"):
    _client = QdrantClient(url=settings.qdrant_url)
else:
    # Embedded mode: runs Qdrant in-process, storing data on disk. No server/Docker needed.
    _client = QdrantClient(path=settings.qdrant_url)


def ensure_collection(collection_name: str) -> None:
    if not _client.collection_exists(collection_name):
        _client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=settings.embedding_dim, distance=Distance.COSINE),
        )


def upsert_chunks(
    collection_name: str, doc_id: str, filename: str, chunks_with_vectors: list[tuple]
) -> None:
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "doc_id": doc_id,
                "filename": filename,
                "page": chunk.page,
                "text": chunk.text,
            },
        )
        for chunk, vector in chunks_with_vectors
    ]
    _client.upsert(collection_name=collection_name, points=points)


def delete_collection(collection_name: str) -> None:
    if _client.collection_exists(collection_name):
        _client.delete_collection(collection_name)


def search(collection_name: str, query_vector: list[float], top_k: int) -> list[dict]:
    if not _client.collection_exists(collection_name):
        return []
    results = _client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
    ).points
    return [
        {
            "score": point.score,
            "filename": point.payload["filename"],
            "page": point.payload["page"],
            "text": point.payload["text"],
        }
        for point in results
    ]
