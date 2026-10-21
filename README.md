# Experimento controlado Text-to-SQL

Implementação reproduzível para comparar contexto técnico e contexto semântico, mantendo agente, modelo, perguntas, snapshot e parâmetros constantes. A base padrão é `commercial`, uma base comercial descaracterizada autorizada pelo responsável do estudo. `synthetic_commercial` permanece para testes automatizados.

## Execução

1. Copie `.env.example` para `.env` e ajuste credenciais. Suba `docker compose up -d`.
2. Execute `make assess-data`, `make setup`, `make test`, `make pilot`, `make experiment`, `make analyze`.

O provedor padrão é determinístico e serve a testes de ponta a ponta. Para um provedor OpenAI compatível, defina `LLM_PROVIDER=openai`, `OPENAI_API_KEY` e `LLM_MODEL`. Não envie dados das candidatas externas ao provedor.

Registros são acrescentados em `artifacts/raw/`; não são sobrescritos. Consulte `docs/decisions.md` para o protocolo e limitações.

## Estado do projeto

Consulte [`docs/status.md`](docs/status.md) para o ponto de parada, o que já foi concluído e os próximos passos.
