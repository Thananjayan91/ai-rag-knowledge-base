import os
import tempfile
from pathlib import Path

_TEST_DATA_DIR = Path(tempfile.mkdtemp(prefix="rag_kb_test_"))
os.environ.setdefault("OPENAI_API_KEY", "sk-test")
os.environ["QDRANT_URL"] = str(_TEST_DATA_DIR / "qdrant_data")

import pytest  # noqa: E402

import backend.projects as projects  # noqa: E402

projects.PROJECTS_FILE = _TEST_DATA_DIR / "projects.json"


@pytest.fixture(autouse=True)
def _clean_project_registry():
    if projects.PROJECTS_FILE.exists():
        projects.PROJECTS_FILE.unlink()
    yield
