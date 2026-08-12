from backend.chunking import chunk_pages
from backend.extraction import ExtractedPage


def test_chunk_pages_splits_long_text_with_overlap():
    page = ExtractedPage(page=1, text=" ".join(f"word{i}" for i in range(1000)))
    chunks = chunk_pages([page], chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(c.page == 1 for c in chunks)


def test_chunk_pages_short_text_stays_single_chunk():
    page = ExtractedPage(page=1, text="short text")
    chunks = chunk_pages([page], chunk_size=500, overlap=50)
    assert len(chunks) == 1
    assert chunks[0].text.strip() == "short text"


def test_chunk_pages_empty_input_returns_empty():
    assert chunk_pages([], chunk_size=500, overlap=50) == []


def test_chunk_pages_preserves_page_number_across_chunks():
    page = ExtractedPage(page=7, text=" ".join(f"tok{i}" for i in range(500)))
    chunks = chunk_pages([page], chunk_size=50, overlap=10)
    assert len(chunks) > 1
    assert all(c.page == 7 for c in chunks)
