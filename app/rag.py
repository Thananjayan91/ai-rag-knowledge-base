import uuid

from openai import OpenAI

from app.chunking import chunk_pages
from app.config import settings
from app.embeddings import embed_text, embed_texts
from app.extraction import extract_document
from app.projects import collection_name as project_collection
from app.reranking import rerank
from app.vector_store import ensure_collection, search, upsert_chunks

_client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using only the provided context. "
    "If the context does not contain the answer, say you don't know. "
    "Always cite sources inline using the [Source N] markers shown in the context."
)


def ingest_document(project_slug: str, file_path: str, filename: str) -> dict:
    collection = project_collection(project_slug)
    ensure_collection(collection)
    pages = extract_document(file_path, filename)
    if not pages:
        raise ValueError("No extractable text found in document")

    chunks = chunk_pages(pages, settings.chunk_size_tokens, settings.chunk_overlap_tokens)
    vectors = embed_texts([chunk.text for chunk in chunks])

    doc_id = str(uuid.uuid4())
    upsert_chunks(collection, doc_id, filename, list(zip(chunks, vectors)))

    return {"doc_id": doc_id, "filename": filename, "chunks_indexed": len(chunks)}


def answer_question(project_slug: str, question: str, top_k: int | None = None) -> dict:
    collection = project_collection(project_slug)
    query_vector = embed_text(question)
    final_k = top_k or settings.top_k
    candidates = search(collection, query_vector, settings.retrieval_candidates)
    matches = rerank(question, candidates, final_k)

    sources = [
        {
            "filename": m["filename"],
            "page": m["page"],
            "score": round(m["score"], 4),
            "rerank_score": round(m["rerank_score"], 4),
        }
        for m in matches
    ]

    if not matches:
        return {
            "answer": "I don't have any documents indexed for this project yet.",
            "sources": sources,
        }

    context_blocks = []
    for i, match in enumerate(matches, start=1):
        location = f"page {match['page']}" if match["page"] else match["filename"]
        context_blocks.append(f"[Source {i} - {match['filename']}, {location}]\n{match['text']}")
    context = "\n\n".join(context_blocks)

    completion = _client.chat.completions.create(
        model=settings.chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    answer = completion.choices[0].message.content

    return {"answer": answer, "sources": sources}
