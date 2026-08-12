from pathlib import Path

import pdfplumber
import requests
from bs4 import BeautifulSoup
from docx import Document


class ExtractedPage:
    def __init__(self, page: int | None, text: str):
        self.page = page
        self.text = text


def extract_pdf(file_path: str) -> list[ExtractedPage]:
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(ExtractedPage(page=i, text=text))
    return pages


def extract_docx(file_path: str) -> list[ExtractedPage]:
    doc = Document(file_path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [ExtractedPage(page=None, text=text)] if text.strip() else []


def extract_txt(file_path: str) -> list[ExtractedPage]:
    text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    return [ExtractedPage(page=None, text=text)] if text.strip() else []


def extract_url(url: str) -> list[ExtractedPage]:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    text = "\n".join(lines)
    return [ExtractedPage(page=None, text=text)] if text.strip() else []


def extract_document(file_path: str, filename: str) -> list[ExtractedPage]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(file_path)
    if suffix == ".docx":
        return extract_docx(file_path)
    if suffix == ".txt":
        return extract_txt(file_path)
    raise ValueError(f"Unsupported file type: {suffix}")
