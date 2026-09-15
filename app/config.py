"""Application configuration loaded from environment variables and .env file."""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3.5:4b")
    OLLAMA_TIMEOUT: float = float(os.getenv("OLLAMA_TIMEOUT", "60.0"))
    SEMANTIC_SCHOLAR_API_KEY: str | None = os.getenv("SEMANTIC_SCHOLAR_API_KEY") or None
    CORE_API_KEY: str | None = os.getenv("CORE_API_KEY") or None
    NCBI_API_KEY: str | None = os.getenv("NCBI_API_KEY") or None
    OPENALEX_EMAIL: str | None = os.getenv("OPENALEX_EMAIL") or None
    SEARCH_TIMEOUT_SECONDS: float = float(os.getenv("SEARCH_TIMEOUT_SECONDS", "15.0"))
    MAX_SEARCH_RESULTS_PER_SOURCE: int = int(os.getenv("MAX_SEARCH_RESULTS_PER_SOURCE", "10"))
    MAX_RESEARCH_ITERATIONS: int = int(os.getenv("MAX_RESEARCH_ITERATIONS", "6"))
    MAX_PAPERS_TOTAL: int = int(os.getenv("MAX_PAPERS_TOTAL", "30"))
    FULL_TEXT_TIMEOUT_SECONDS: float = float(os.getenv("FULL_TEXT_TIMEOUT_SECONDS", "30.0"))
    FULL_TEXT_CHUNK_CHARS: int = int(os.getenv("FULL_TEXT_CHUNK_CHARS", "3500"))
    FULL_TEXT_OVERLAP_CHARS: int = int(os.getenv("FULL_TEXT_OVERLAP_CHARS", "350"))
    FULL_TEXT_CACHE_DIR: Path = PROJECT_ROOT / ".cache" / "full_text"
    REPORTS_DIR: Path = PROJECT_ROOT / "reports"


config = Config()
