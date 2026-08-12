# ai-rag-knowledge-base

RAG pipeline: PDF/DOCX/TXT → extraction → chunking → embeddings → Qdrant → retrieval → reranking → LLM → answer with page citations.

See [HOW_TO_RUN.md](HOW_TO_RUN.md) for step-by-step setup, run, and troubleshooting instructions.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # then fill in OPENAI_API_KEY
```

Qdrant runs embedded (in-process, storing data under `./qdrant_data`) by default — no server or Docker required for local dev. To use a real Qdrant server instead (e.g. for Docker/production), set `QDRANT_URL=http://localhost:6333` in `.env` and run:

```bash
docker compose up -d
```

## Run

```bash
uvicorn app.main:app --reload            # API at http://localhost:8000/docs
streamlit run ui/streamlit_app.py        # UI at http://localhost:8501
```

Upload a PDF in the sidebar, then ask a question — the answer comes back with filename + page citations.

## Status

Multi-project ingestion + retrieval + cross-encoder reranking (`cross-encoder/ms-marco-MiniLM-L-6-v2`, local, no API cost) + citations. Each project is an isolated Qdrant collection. No Postgres metadata store yet.

Next: Postgres for document metadata, Docker Compose for the full app, React/Next.js UI.