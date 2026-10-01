import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from backend.history import append_chat_message, clear_chat_history, delete_chat_history_file, get_chat_history
from backend.projects import collection_name, create_project, delete_project, get_project, list_projects
from backend.rag import answer_question, ingest_document
from backend.vector_store import delete_collection


import asyncio
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.reranking import _get_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm CrossEncoder model in background thread on startup so first query doesn't lag
    asyncio.get_event_loop().run_in_executor(None, _get_model)
    yield

app = FastAPI(title="AI RAG Knowledge Base", lifespan=lifespan)


static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def read_index():
    return FileResponse(static_dir / "index.html")


ALLOWED_SUFFIXES = {".pdf", ".docx", ".txt"}


class ProjectCreateRequest(BaseModel):
    name: str


class AskRequest(BaseModel):
    project: str
    question: str
    top_k: int | None = None


def _require_project(slug: str) -> None:
    if get_project(slug) is None:
        raise HTTPException(404, f"Unknown project: {slug}")


@app.get("/projects")
async def get_projects():
    return list_projects()


@app.post("/projects")
async def post_project(request: ProjectCreateRequest):
    try:
        return create_project(request.name)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.delete("/projects/{slug}")
async def remove_project(slug: str):
    _require_project(slug)
    delete_collection(collection_name(slug))
    delete_project(slug)
    delete_chat_history_file(slug)
    return {"deleted": slug}


@app.post("/documents/upload")
async def upload_document(project: str = Form(...), file: UploadFile = File(...)):
    _require_project(project)

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(400, f"Unsupported file type: {suffix}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = ingest_document(project, tmp_path, file.filename)
    except ValueError as e:
        raise HTTPException(400, str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return result


@app.get("/history/{slug}")
async def get_history(slug: str):
    _require_project(slug)
    return get_chat_history(slug)


@app.delete("/history/{slug}")
async def clear_history(slug: str):
    _require_project(slug)
    clear_chat_history(slug)
    return {"status": "cleared", "project": slug}


@app.post("/ask")
async def ask(request: AskRequest):
    _require_project(request.project)
    result = answer_question(request.project, request.question, request.top_k)
    # Save conversation turn to persistent JSON history
    append_chat_message(request.project, request.question, result["answer"], result.get("sources", []))
    return result


@app.get("/health")
async def health():
    return {"status": "ok"}

