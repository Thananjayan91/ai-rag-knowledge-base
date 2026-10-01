# AI RAG Knowledge Base

Multi-project RAG (Retrieval-Augmented Generation) knowledge base. Create isolated projects (CV, Company SOP, Portfolio, etc.), upload PDF/DOCX/TXT files, and ask questions that get answered with inline citations (filename, page number, and similarity/rerank scores).

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

- **`backend/`** — FastAPI application implementing the pipeline, serving the REST API and the integrated Single-Page Web UI.
- **`backend/static/`** — Built-in responsive HTML5 / CSS3 / JavaScript single-page application.
- **`frontend/`** — Optional Streamlit UI.
- **Qdrant** — Runs embedded (in-process on-disk) by default, or connectable to a standalone server via Docker (`docker-compose.yml`).

## Features

- **Multi-Project Isolation** — Each project (e.g. "My CV", "Company SOPs", "Research") gets its own dedicated Qdrant collection so contexts never bleed into each other.
- **Single Unified App & Modern Web UI** — Unified FastAPI server serving both REST endpoints and a clean, responsive chat UI with typing indicators and real-time status.
- **Cross-Encoder Reranking** — Local HuggingFace cross-encoder (`ms-marco-MiniLM-L-6-v2`) reranks initial vector candidates to ensure maximum relevance without extra API costs.
- **Background Pre-warming** — Reranker model pre-warms on startup in a background thread to prevent query timeouts.
- **Multi-File Document Upload** — Index `.pdf`, `.docx`, and `.txt` files with token-based overlapping chunking.
- **Detailed Source Citations** — Inline source tags showing filename, page number, raw similarity score, and reranker score.

## Tech Stack

| Layer | Choice |
|---|---|
| Backend API & UI Server | Python, FastAPI |
| Web UI | HTML5, CSS3, JavaScript (Bootstrap 5, Icons) / Streamlit |
| Embeddings + LLM | OpenAI (`text-embedding-3-small`, `gpt-4o-mini`) |
| Vector Store | Qdrant (Embedded local on-disk or Docker server) |
| Reranking | `sentence-transformers` Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) |
| Text Extraction | `pdfplumber`, `python-docx` |
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

### Running the App (Single Unified Server)

Start the FastAPI application:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

- **Web UI:** Open [http://localhost:8000](http://localhost:8000) in your browser.
- **Swagger API Docs:** Available at [http://localhost:8000/docs](http://localhost:8000/docs).

*(Optional Streamlit UI can still be run via `streamlit run frontend/streamlit_app.py`)*

## Environment Variables

Set in `.env` (see `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | Project-scoped API key from platform.openai.com/api-keys |
| `QDRANT_URL` | `./qdrant_data` | Local folder path for embedded Qdrant, or `http://localhost:6333` for Docker |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `CHAT_MODEL` | `gpt-4o-mini` | OpenAI chat model used to generate answers |

## Running Qdrant in Docker (Optional for Concurrent Access)

If you need multi-process or multi-instance access:

```bash
docker compose up -d
```

Update your `.env`:
```env
QDRANT_URL=http://localhost:6333
```

## API Documentation

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serves the web UI |
| `GET` | `/projects` | List all projects |
| `POST` | `/projects` | Create a project (`{"name": "..."}`) |
| `DELETE` | `/projects/{slug}` | Delete a project, its vector index, and its chat history |
| `POST` | `/documents/upload` | Upload & index file into a project (`project`, `file`) |
| `GET` | `/history/{slug}` | Get saved chat history for a project |
| `DELETE` | `/history/{slug}` | Clear chat history for a project |
| `POST` | `/ask` | Query knowledge base & record to history (`{"project": "...", "question": "..."}`) |
| `GET` | `/health` | Liveness check |


## Testing

```bash
pip install -r requirements-dev.txt
pytest
```
