# Experimento controlado Text-to-SQL

Implementação reproduzível para comparar contexto técnico e contexto semântico, mantendo agente, modelo, perguntas, snapshot e parâmetros constantes. A base padrão é `commercial`, uma base comercial descaracterizada autorizada pelo responsável do estudo. `synthetic_commercial` permanece para testes automatizados.

## Execução

1. Copie `.env.example` para `.env` e ajuste credenciais. Suba `docker compose up -d`.
2. Execute `make assess-data`, `make setup`, `make test`, `make pilot`, `make experiment`, `make analyze`.

O provedor padrão é determinístico e serve a testes de ponta a ponta. Para um provedor OpenAI compatível, defina `LLM_PROVIDER=openai`, `OPENAI_API_KEY`, `OPENAI_BASE_URL` e `LLM_MODEL`. Não envie dados das candidatas externas ao provedor.

### Provedor LLM gratuito (Groq)

O experimento usa a API gratuita do [Groq](https://console.groq.com) (compatível com o padrão OpenAI, sem cartão de crédito). Após gerar a API key:

```
LLM_PROVIDER=openai
LLM_MODEL=openai/gpt-oss-120b
OPENAI_API_KEY=gsk_...
OPENAI_BASE_URL=https://api.groq.com/openai/v1
```

Modelos sugeridos (catálogo em https://console.groq.com/docs/models, validado em 14/11/2026): `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`. Para reprodutibilidade, o experimento fixa `temperature=0`.

Registros são acrescentados em `artifacts/raw/`; não são sobrescritos. Consulte `docs/decisions.md` para o protocolo e limitações.

## Estado do projeto

Consulte [`docs/status.md`](docs/status.md) para o ponto de parada, o que já foi concluído e os próximos passos.
