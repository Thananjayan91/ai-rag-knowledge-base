import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from backend.projects import collection_name, create_project, delete_project, get_project, list_projects
from backend.rag import answer_question, ingest_document
from backend.vector_store import delete_collection

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="AI RAG Knowledge Base")

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


@app.post("/ask")
async def ask(request: AskRequest):
    _require_project(request.project)
    return answer_question(request.project, request.question, request.top_k)


@app.get("/health")
async def health():
    return {"status": "ok"}
