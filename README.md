# AI RAG Knowledge Base

Multi-project RAG (Retrieval-Augmented Generation) knowledge base. Create a project, upload any number of PDF/DOCX/TXT files, and ask questions that get answered from just those files — with citations back to the source filename and page number.

## Live Demo

Not yet deployed. Runs locally in a few minutes — see [Local Installation](#local-installation).

## Demo Video

Coming soon.

## Architecture

```
PDF / DOCX / TXT
      │
      ▼
Text extraction (pdfplumber / python-docx)
      │
      ▼
Chunking (tiktoken, overlapping windows)
      │
      ▼
Embeddings (OpenAI text-embedding-3-small)
      │
      ▼
Qdrant  ──── one isolated collection per project
      │
      ▼
Retrieval (top-20 by cosine similarity)
      │
      ▼
Reranking (local cross-encoder, ms-marco-MiniLM-L-6-v2)
      │
      ▼
LLM (OpenAI gpt-4o-mini)
      │
      ▼
Answer + source citations (filename, page, score)
```

- **`backend/`** — FastAPI service implementing the pipeline above, exposed as a small REST API
- **`frontend/`** — Streamlit UI for creating projects, uploading documents, and asking questions
- **Qdrant** runs embedded (in-process, on-disk) by default — no separate server needed for local dev

## Features

- Multiple isolated knowledge-base "projects" — each gets its own Qdrant collection, so questions in one project never see documents from another
- Multi-file upload — select and index any number of PDF/DOCX/TXT files in one action
- Cross-encoder reranking to fix the common RAG failure where raw embedding similarity can't reliably separate relevant from irrelevant chunks
- Answers cite filename + page number, and show both the raw similarity and rerank score for every retrieved chunk
- Project deletion (with confirmation) to clear out a knowledge base and start over

## Tech Stack

| Layer | Choice |
|---|---|
| Backend API | Python, FastAPI |
| Frontend | Streamlit |
| Embeddings + LLM | OpenAI (`text-embedding-3-small`, `gpt-4o-mini`) |
| Vector store | Qdrant (embedded by default; swappable for a real server) |
| Reranking | `sentence-transformers` cross-encoder (local, no API cost) |
| Text extraction | `pdfplumber`, `python-docx` |
| Testing | `pytest` |

## Local Installation

```bash
git clone https://github.com/Thananjayan91/ai-rag-knowledge-base.git
cd ai-rag-knowledge-base
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # then fill in OPENAI_API_KEY
```

Run it (two terminals):

```bash
uvicorn backend.main:app --reload        # API at http://localhost:8000/docs
streamlit run frontend/streamlit_app.py  # UI at http://localhost:8501
```

Full walkthrough, including troubleshooting common errors, is in [docs/HOW_TO_RUN.md](docs/HOW_TO_RUN.md).

## Environment Variables

Set in `.env` (see `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | Project-scoped API key from platform.openai.com/api-keys |
| `QDRANT_URL` | `./qdrant_data` | Local folder path for embedded Qdrant, or an `http://` URL for a real Qdrant server |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `CHAT_MODEL` | `gpt-4o-mini` | OpenAI chat model used to generate answers |

## API Documentation

Interactive Swagger UI is auto-generated at `http://localhost:8000/docs` once the backend is running. Main endpoints:

| Method | Path | Description |
|---|---|---|
| `GET` | `/projects` | List all projects |
| `POST` | `/projects` | Create a project (`{"name": "..."}`) |
| `DELETE` | `/projects/{slug}` | Delete a project and its indexed documents |
| `POST` | `/documents/upload` | Upload + index a file into a project (multipart form: `project`, `file`) |
| `POST` | `/ask` | Ask a question (`{"project": "...", "question": "..."}`) |
| `GET` | `/health` | Liveness check |

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

28 tests covering chunking, text extraction, project lifecycle, reranking logic, and the full API (project CRUD, upload validation, and an end-to-end ingest→ask flow). OpenAI calls are mocked in tests — running the suite costs nothing and needs no real API key.

## Future Improvements

- Containerize with Docker (`Dockerfile` + full `docker-compose.yml` covering backend, frontend, and Qdrant)
- Postgres for document/project metadata instead of a local JSON file
- Authentication and per-user project scoping
- Per-document deletion/re-indexing (currently only whole-project deletion)
- Deploy a live demo (Streamlit Community Cloud + Qdrant Cloud free tier)
- React/Next.js frontend

## Known Limitations

- **Single-process Qdrant access** — embedded mode allows only one process to open `qdrant_data` at a time; a real Qdrant server is needed for multi-instance deployment
- **No authentication** — anyone who can reach the API can create, query, or delete any project
- **Blocking calls in async routes** — OpenAI and reranker calls run synchronously inside `async def` endpoints, which limits request concurrency under load; needs to move to a thread pool or async clients before scaling up
- **No rate limiting or upload size caps**
