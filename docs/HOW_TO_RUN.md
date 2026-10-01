# How to Run

## 1. First-Time Setup

```bash
cd ai-rag-knowledge-base
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and set `OPENAI_API_KEY` to your project-scoped API key from https://platform.openai.com/api-keys.

No external databases needed by default — Qdrant runs embedded and stores vector data in `./qdrant_data`.

---

## 2. Start the App

Start the unified FastAPI server:

```bash
.venv\Scripts\activate
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

- **Web UI:** Open [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs:** Open [http://localhost:8000/docs](http://localhost:8000/docs)

*(Optional: If you prefer the Streamlit interface, run `streamlit run frontend/streamlit_app.py`)*

---

## 3. How to Use

Each **project** acts as a completely isolated knowledge base (e.g. "My CV", "Company SOPs", "Product Portfolios"):

1. In the sidebar under **Projects**, click **+ New**, enter a name, and click **Create**.
2. Select your newly created project from the list.
3. In the **Upload Documents** box, select your PDF/DOCX/TXT files and click **Index Document(s)**.
4. Type your question in the chat input and hit **Ask** (or press `Enter`).
5. Receive answers with source citations, page numbers, similarity scores, and reranker scores!

---

## 4. Concurrent Access with Docker (Optional)

If multiple processes need concurrent access to Qdrant without local file locks:

```bash
docker compose up -d
```

Set in `.env`:
```env
QDRANT_URL=http://localhost:6333
```

---

## 5. Troubleshooting

- **`AuthenticationError` / `not_authorized_invalid_key_type`**: Ensure your OpenAI key is a valid project-scoped API key.
- **`Unsupported file type`**: Currently `.pdf`, `.docx`, and `.txt` are supported.
- **`Storage folder is already accessed by another instance`**: Embedded Qdrant only allows one local process at a time. Make sure you only run one instance of `uvicorn`, or switch to Docker Qdrant (`http://localhost:6333`).
- **Initial Query Delay**: The Cross-Encoder model is downloaded and pre-warmed on server startup in the background. Once cached, answers return rapidly.
