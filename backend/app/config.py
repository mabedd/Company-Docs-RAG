from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Company Docs RAG"
    chroma_path: str = "./data/chroma"
    collection_name: str = "company_docs"
    chunk_size: int = 800
    chunk_overlap: int = 120
    top_k: int = 5
    min_relevance_score: float = 0.18
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"


settings = Settings()
