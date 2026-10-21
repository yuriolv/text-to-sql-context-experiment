from __future__ import annotations
import os
from pathlib import Path
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
class Settings(BaseModel):
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "postgresql://tcc_owner:change_me@localhost:5432/tccsql"))
    readonly_database_url: str = Field(default_factory=lambda: os.getenv("READONLY_DATABASE_URL", "postgresql://tcc_reader:change_me@localhost:5432/tccsql"))
    llm_provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "fake"))
    llm_model: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "fake-deterministic-v1"))
    experiment_version: str = Field(default_factory=lambda: os.getenv("EXPERIMENT_VERSION", "1.0.0"))
    timeout_ms: int = 5000
    max_result_rows_for_model: int = 5
def settings() -> Settings: return Settings()
