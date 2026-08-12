from sentence_transformers import CrossEncoder

from app.config import settings

_model: CrossEncoder | None = None


def _get_model() -> CrossEncoder:
    global _model
    if _model is None:
        _model = CrossEncoder(settings.reranker_model)
    return _model


def rerank(question: str, matches: list[dict], top_n: int) -> list[dict]:
    if not matches:
        return matches

    pairs = [(question, m["text"]) for m in matches]
    scores = _get_model().predict(pairs)

    for match, score in zip(matches, scores):
        match["rerank_score"] = float(score)

    matches.sort(key=lambda m: m["rerank_score"], reverse=True)
    return matches[:top_n]
