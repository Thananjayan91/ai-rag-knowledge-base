import tiktoken

from app.extraction import ExtractedPage

_encoding = tiktoken.get_encoding("cl100k_base")


class Chunk:
    def __init__(self, text: str, page: int | None, chunk_index: int):
        self.text = text
        self.page = page
        self.chunk_index = chunk_index


def chunk_pages(pages: list[ExtractedPage], chunk_size: int, overlap: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    for page in pages:
        tokens = _encoding.encode(page.text)
        start = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_text = _encoding.decode(tokens[start:end])
            chunks.append(Chunk(text=chunk_text, page=page.page, chunk_index=len(chunks)))
            if end == len(tokens):
                break
            start = end - overlap
    return chunks
