from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    openai_api_key: str
    qdrant_url: str = "./qdrant_data"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    chat_model: str = "gpt-4o-mini"
    chunk_size_tokens: int = 500
    chunk_overlap_tokens: int = 75
    top_k: int = 5
    retrieval_candidates: int = 20
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"


settings = Settings()
