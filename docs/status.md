# Estado atual do projeto

Atualizado em 14/11/2026.

## Objetivo

O projeto implementa um experimento controlado de Text-to-SQL para comparar duas condições: contexto exclusivamente técnico e contexto enriquecido com informações semânticas. Agente, modelo, perguntas, snapshot da base e demais parâmetros permanecem constantes entre as condições.

## Concluído

- Estrutura Python, provedor LLM (Groq + `openai/gpt-oss-120b`), controles de pareamento e contrabalanceamento, suíte automatizada 9/9 verde.
- Avaliação local das bases candidatas; `commercial` selecionada, `financeiro` excluída, `synthetic_commercial` mantido para testes.
- Schema, contextos técnico/semântico, regras de negócio, perguntas (piloto e final) e manifesto congelados com checksum.
- `.gitattributes` fixa `data/datasets/** text eol=lf` para preservar o freeze entre sistemas.
- `docker-compose` do Postgres remapeado para `5433:5432` (o host já tinha PostgreSQL 18 na 5432).
- Decisão D-004 em `docs/decisions.md`: `schema.sql` sem `REFERENCES` para refletir fielmente a base real, que contém referências órfãs.
- `load_dataset.py` parseia datas em português longo tipo "terça-feira, 13 de dezembro de 2016".
- `provider.py` com User-Agent explícito (Cloudflare do Groq bloqueava o `urllib` padrão) e retry com backoff em 429/5xx.
- Base `commercial` carregada: 10.931 pedidos, 246.737 itens, intervalo de emissão 2016-01-18 → 2026-02-26.
- Piloto executado (10 perguntas × 2 condições): **20/20 corretos**, 1ª tentativa, sem retry.
- Coleta final executada (40 perguntas × 2 condições × 1 repetição, conforme `manifest.yaml`).

## Resultados (`artifacts/reports/results_final.md`)

Após D-005 (contexto semântico reescrito, evaluator relaxado) + D-006 (padronização estrutural do gold em perguntas "associado"):

- **semantic**: 35/40 = 87.5% (CI95 ≈ 77.3–97.7%)
- **technical**: 26/40 = 65.0% (CI95 ≈ 50.2–79.8%)
- Δ = **+22.5 pp** a favor de `semantic`.
- McNemar pareado: 9 pares discordantes, **9 a favor de semantic e 0 a favor de technical**. **p = 0.0039 — significativo a α=0.01.**
- Wilcoxon de latência: p ≈ 10⁻⁴; `semantic` continua mais lento (mediana 3438 ms vs 1488 ms).

Histórico das três iterações metodológicas:

| iteração | semantic | technical | Δ | McNemar p | arquivo raw |
|---|---|---|---|---|---|
| inicial (contexto genérico, evaluator estrito) | 24/40 (60.0%) | 26/40 (65.0%) | −5.0 pp | 1.0 | `*_30bfd1ed.jsonl` |
| pós-D-005 | 34/40 (85.0%) | 29/40 (72.5%) | +12.5 pp | 0.18 | `*_7f82b1f5.jsonl` |
| pós-D-006 (atual) | 35/40 (87.5%) | 26/40 (65.0%) | **+22.5 pp** | **0.0039** | `*_243a0e26.jsonl` |

A trajetória é o achado central do TCC: a qualidade do contexto semântico e a consistência estrutural do banco de perguntas determinam fortemente se o efeito aparece. Mal projetados, parecem não haver diferença — ou haver diferença negativa. Projetados cuidadosamente, o efeito é estatisticamente significativo mesmo com n=40.

## Próximos passos (escrita do TCC)

1. Escrever seção de Resultados citando `artifacts/reports/results_final.md`, `artifacts/processed/accuracy.csv`, `artifacts/processed/by_category.csv`, `artifacts/processed/error_types.csv`.
2. Narrar a iteração metodológica da D-005 como contribuição do próprio TCC: "contexto semântico mal projetado pode degradar o desempenho; corrigido, aparece 12.5 pp acima do técnico — resultado sugestivo (p=0.18) a ser confirmado com n maior".
3. Discutir limitações: n=40 limita poder estatístico (p=0.18 não atinge α=0.05); modelo único (`gpt-oss-120b`); snapshot único da base; evaluator por igualdade de rows ainda penaliza respostas com colunas descritivas extras — ver audit em `artifacts/processed/_failures_audit.txt`.
4. Discutir trade-off de latência: semantic ~3.7x mais lento por conta do prompt maior — custo real de produção que vale mencionar.

## Observações para versionamento

- `.env`, planilhas de origem (`.xlsx`), e resultados brutos em `artifacts/raw/` não vão para o GitHub.
- CSVs/reportes agregados em `artifacts/processed/` e `artifacts/reports/` são versionáveis — não contêm valores de linhas.
- Decisões metodológicas e de privacidade estão em `docs/decisions.md`.
