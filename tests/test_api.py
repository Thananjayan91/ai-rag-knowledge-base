from fastapi.testclient import TestClient

import backend.rag as rag
from backend.main import app

client = TestClient(app)

FAKE_VECTOR_DIM = 1536


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_project_lifecycle_create_list_delete():
    response = client.post("/projects", json={"name": "Test Project"})
    assert response.status_code == 200
    assert response.json() == {"slug": "test-project", "name": "Test Project"}

    response = client.get("/projects")
    assert {"slug": "test-project", "name": "Test Project"} in response.json()

    response = client.delete("/projects/test-project")
    assert response.status_code == 200

    response = client.get("/projects")
    assert response.json() == []


def test_delete_unknown_project_returns_404():
    response = client.delete("/projects/does-not-exist")
    assert response.status_code == 404


def test_ask_unknown_project_returns_404():
    response = client.post("/ask", json={"project": "nope", "question": "hi"})
    assert response.status_code == 404


def test_upload_unknown_project_returns_404():
    response = client.post(
        "/documents/upload",
        data={"project": "nope"},
        files={"file": ("note.txt", b"content", "text/plain")},
    )
    assert response.status_code == 404


def test_upload_rejects_unsupported_file_type():
    client.post("/projects", json={"name": "Upload Test"})
    response = client.post(
        "/documents/upload",
        data={"project": "upload-test"},
        files={"file": ("test.exe", b"binary", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_full_ingest_and_ask_flow(monkeypatch):
    monkeypatch.setattr(
        rag, "embed_texts", lambda texts: [[0.1] * FAKE_VECTOR_DIM for _ in texts]
    )
    monkeypatch.setattr(rag, "embed_text", lambda text: [0.1] * FAKE_VECTOR_DIM)

    class _FakeMessage:
        def __init__(self, content):
            self.content = content

    class _FakeChoice:
        def __init__(self, content):
            self.message = _FakeMessage(content)

    class _FakeCompletion:
        def __init__(self, content):
            self.choices = [_FakeChoice(content)]

    monkeypatch.setattr(
        rag._client.chat.completions,
        "create",
        lambda **kwargs: _FakeCompletion("This is a test answer [Source 1]."),
    )

    client.post("/projects", json={"name": "Flow Test"})

    upload_response = client.post(
        "/documents/upload",
        data={"project": "flow-test"},
        files={"file": ("note.txt", b"Some test content about widgets.", "text/plain")},
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["chunks_indexed"] >= 1

    ask_response = client.post(
        "/ask", json={"project": "flow-test", "question": "What is this about?"}
    )
    assert ask_response.status_code == 200
    body = ask_response.json()
    assert body["answer"] == "This is a test answer [Source 1]."
    assert len(body["sources"]) >= 1
