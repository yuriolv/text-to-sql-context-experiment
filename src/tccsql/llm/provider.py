from __future__ import annotations
from dataclasses import dataclass
from time import perf_counter, sleep
from typing import Protocol
import os, requests
@dataclass(frozen=True)
class Message: role: str; content: str
@dataclass(frozen=True)
class ModelResponse: text: str; model: str; input_tokens: int|None; output_tokens: int|None; latency_ms: float; request_id: str|None=None
class Provider(Protocol):
    def generate(self, messages: list[Message], configuration: dict) -> ModelResponse: ...
class FakeProvider:
    """Resposta fixa e segura para testes; nunca consulta dados externos."""
    def generate(self, messages, configuration):
        question = next((m.content for m in messages if m.role == "user"), "")
        sql = "SELECT 1 AS unsupported_question" if "SQL" not in question else "SELECT 1 AS result"
        return ModelResponse(sql, "fake-deterministic-v1", sum(len(m.content.split()) for m in messages), len(sql.split()), 0.0, "fake")
class OpenAICompatibleProvider:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key, self.base_url, self.model = api_key, base_url.rstrip("/"), model
    def generate(self, messages, configuration):
        payload = {"model": self.model, "messages": [m.__dict__ for m in messages], **configuration}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "User-Agent": "tccsql-experiment/1.0", "Connection": "close"}
        started = perf_counter()
        for attempt in range(6):
            try:
                response = requests.post(self.base_url + "/chat/completions", json=payload, headers=headers, timeout=(10, 45))
                if response.status_code in (429, 500, 502, 503) and attempt < 5:
                    retry_after = response.headers.get("Retry-After")
                    wait = float(retry_after) if retry_after and retry_after.replace(".", "", 1).isdigit() else min(30, 2 ** attempt + 1)
                    sleep(wait); continue
                response.raise_for_status()
                body = response.json()
                request_id = response.headers.get("x-request-id")
                break
            except (requests.ConnectionError, requests.Timeout) as error:
                if attempt < 5:
                    sleep(min(15, 2 ** attempt + 1)); continue
                raise
        usage = body.get("usage", {}); text = body["choices"][0]["message"]["content"]
        return ModelResponse(text, body.get("model", self.model), usage.get("prompt_tokens"), usage.get("completion_tokens"), (perf_counter() - started) * 1000, request_id)
def provider_from_settings(s):
    if s.llm_provider == "fake": return FakeProvider()
    if s.llm_provider == "openai": return OpenAICompatibleProvider(os.environ["OPENAI_API_KEY"], os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"), s.llm_model)
    raise ValueError(f"Provedor desconhecido: {s.llm_provider}")
