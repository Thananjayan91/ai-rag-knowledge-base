# How to Run

## 1. First-time setup

```bash
cd ai-rag-knowledge-base
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and set `OPENAI_API_KEY` to a project-scoped key from https://platform.openai.com/api-keys (make sure a project is selected top-left before creating it — older account/user-level keys get rejected with a 401).

No Docker or database setup needed — Qdrant runs embedded and stores its data in `./qdrant_data`.

## 2. Start the app (two terminals)

**Terminal 1 — API:**
```bash
.venv\Scripts\activate
uvicorn app.main:app --reload
```
Runs at http://localhost:8000 (Swagger docs at http://localhost:8000/docs).

**Terminal 2 — UI:**
```bash
.venv\Scripts\activate
streamlit run ui/streamlit_app.py
```
Opens at http://localhost:8501.

## 3. Use it

Each **project** is its own isolated knowledge base — documents and questions in one project never mix with another.

1. In the sidebar, expand **+ New project**, give it a name (e.g. "Sri Lanka Tourism"), and click **Create project**.
2. Pick it from the **Active project** dropdown.
3. Select one or more PDF/DOCX/TXT files in the uploader and click **Index N document(s)** — all of them get embedded and stored under this project.
4. Type a question in the main box and click **Ask** — the answer is drawn from every file indexed under the selected project.
5. The answer appears with a **Sources** list showing filename + page number for each citation.

Repeat step 1–2 to create more projects (e.g. "Company Policies") and switch between them from the same dropdown.

## Troubleshooting

- **`AuthenticationError` / `not_authorized_invalid_key_type`** — the key in `.env` isn't a valid project API key. Generate a new one at platform.openai.com/api-keys with a project selected, and revoke the old one.
- **`Unsupported file type`** — only `.pdf`, `.docx`, `.txt` are supported right now.
- **Answer says "I don't have any documents indexed for this project yet."** — nothing's been uploaded to the active project yet, or you're looking at the wrong project in the sidebar.
- **Answer says "I don't know" with sources listed below it** — that's the model's own judgment that the retrieved chunks don't actually answer your question; check the sources shown to see what it did find.
- **`Unknown project` error** — the project list (`data/projects.json`) and the vector index (`qdrant_data/`) are both local files; deleting either resets that part of the state independently.
- **`Storage folder ... is already accessed by another instance`** — embedded Qdrant only allows one process to open `qdrant_data` at a time. Make sure only one `uvicorn` instance is running.
- **Port already in use** — another process is on 8000 or 8501; stop it or run with `--port <other-port>`.
