from backend import reranking


class _FakeModel:
    """Scores each pair by text length, so ordering is predictable without a real model."""

    def predict(self, pairs):
        return [len(text) for _, text in pairs]


def test_rerank_orders_by_score_descending(monkeypatch):
    monkeypatch.setattr(reranking, "_get_model", lambda: _FakeModel())
    matches = [
        {"text": "short"},
        {"text": "a much longer piece of text here"},
        {"text": "mid length text"},
    ]

    result = reranking.rerank("question", matches, top_n=3)

    assert [m["text"] for m in result] == [
        "a much longer piece of text here",
        "mid length text",
        "short",
    ]


def test_rerank_truncates_to_top_n(monkeypatch):
    monkeypatch.setattr(reranking, "_get_model", lambda: _FakeModel())
    matches = [{"text": "a"}, {"text": "bb"}, {"text": "ccc"}]

    result = reranking.rerank("question", matches, top_n=2)

    assert len(result) == 2


def test_rerank_empty_matches_returns_empty(monkeypatch):
    monkeypatch.setattr(reranking, "_get_model", lambda: _FakeModel())
    assert reranking.rerank("question", [], top_n=5) == []
