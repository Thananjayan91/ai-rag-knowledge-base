import json
import time
from pathlib import Path

CHAT_DIR = Path("data/chat_history")


def _get_history_file(slug: str) -> Path:
    CHAT_DIR.mkdir(parents=True, exist_ok=True)
    return CHAT_DIR / f"{slug}.json"


def get_chat_history(slug: str) -> list[dict]:
    file_path = _get_history_file(slug)
    if not file_path.exists():
        return []
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return []


def append_chat_message(slug: str, question: str, answer: str, sources: list[dict]) -> None:
    history = get_chat_history(slug)
    message_entry = {
        "id": int(time.time() * 1000),
        "timestamp": time.time(),
        "question": question,
        "answer": answer,
        "sources": sources,
    }
    history.append(message_entry)
    file_path = _get_history_file(slug)
    file_path.write_text(json.dumps(history, indent=2), encoding="utf-8")


def clear_chat_history(slug: str) -> bool:
    file_path = _get_history_file(slug)
    if file_path.exists():
        file_path.write_text(json.dumps([], indent=2), encoding="utf-8")
        return True
    return False


def delete_chat_history_file(slug: str) -> None:
    file_path = _get_history_file(slug)
    if file_path.exists():
        file_path.unlink(missing_ok=True)
