import json
import re
from pathlib import Path

PROJECTS_FILE = Path("data/projects.json")


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    if not slug:
        raise ValueError("Project name must contain at least one letter or number")
    return slug


def _load() -> dict:
    if not PROJECTS_FILE.exists():
        return {}
    return json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))


def _save(projects: dict) -> None:
    PROJECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROJECTS_FILE.write_text(json.dumps(projects, indent=2), encoding="utf-8")


def list_projects() -> list[dict]:
    projects = _load()
    return [{"slug": slug, "name": name} for slug, name in projects.items()]


def get_project(slug: str) -> dict | None:
    projects = _load()
    if slug not in projects:
        return None
    return {"slug": slug, "name": projects[slug]}


def create_project(name: str) -> dict:
    slug = _slugify(name)
    projects = _load()
    if slug not in projects:
        projects[slug] = name
        _save(projects)
    return {"slug": slug, "name": projects[slug]}


def delete_project(slug: str) -> bool:
    projects = _load()
    if slug not in projects:
        return False
    del projects[slug]
    _save(projects)
    return True


def collection_name(slug: str) -> str:
    return f"kb_{slug}"
