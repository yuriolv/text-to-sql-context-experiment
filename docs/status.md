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

## Resultados

Relatórios em `artifacts/reports/results_final_<modelo>[_tiers].md`.

### Ablação de 3 tiers (D-008): `qwen/qwen3.8-27b`

Desenho progressivamente aditivo (technical ⊂ catalog ⊂ semantic), análogo ao benchmark da comunidade Databricks ("Which context improves Genie accuracy most?", 40% → 47% → 97%).

- **technical** (DDL puro): 23/39 = 58.97% (CI95 43.5–74.4%)
- **catalog** (DDL + descrições por tabela e coluna): 24/39 = 61.54% (CI95 46.3–76.8%)
- **semantic** (catalog + regras de grão + temporais + referenciais + estilo + sinônimos): **34/39 = 87.18%** (CI95 76.7–97.7%)

McNemar pareado:

- technical vs catalog: 1:2 discordantes, **p = 1.0** — adicionar apenas comentários de catálogo não muda acurácia de forma significativa.
- catalog vs semantic: 0:10 discordantes, **p = 0.00195** — adicionar a camada semântica estruturada é o que produz o salto.
- technical vs semantic: 0:11 discordantes, **p = 0.000977** — gap total significativo a α=0.001.

Latência mediana: 2.9 s → 7.7 s → 14.8 s (todas as comparações pareadas significativas, p < 10⁻⁸).

Replicação do shape do benchmark Databricks com modelo open-source e sem Unity Catalog proprietário.

n=39 em vez de 40 por 1 questão com falha de execução SQL em pelo menos uma condição (a linha é descartada do pareamento McNemar/Wilcoxon por não ter dado comparável).

### Modelo principal: `openai/gpt-oss-120b` (Groq)

- **semantic**: 35/40 = 87.5% (CI95 ≈ 77.3–97.7%)
- **technical**: 26/40 = 65.0% (CI95 ≈ 50.2–79.8%)
- Δ = **+22.5 pp** a favor de `semantic`.
- McNemar pareado: 9 pares discordantes, 9:0 a favor de `semantic`. **p = 0.0039** (α=0.01).
- Latência: `semantic` mediana 3438 ms vs `technical` 1488 ms (Wilcoxon p ≈ 10⁻⁴).

### Réplica (validade externa): `qwen/qwen3.8-27b` (Groq)

Mesmo protocolo, mesma base, mesmas perguntas; família de modelo diferente (Alibaba vs OpenAI), tamanho menor (27B vs 120B).

- **semantic**: 34/40 = 85.0% (CI95 ≈ 73.9–96.1%)
- **technical**: 22/40 = 55.0% (CI95 ≈ 39.6–70.4%)
- Δ = **+30.0 pp**.
- McNemar pareado: 12 pares discordantes, 12:0 a favor de `semantic`. **p = 0.00049**.
- Latência: `semantic` mediana ~10.3 s vs `technical` ~3.2 s.

### Pendente — `openai/gpt-oss-120b` para a ablação de 3 tiers

O TPD de 200k tokens/dia da conta Groq esgotou depois dos runs anteriores. Rodar de novo após a próxima virada do dia (UTC).

### Histórico de iterações metodológicas (modelo principal)

| iteração | semantic | technical | Δ | McNemar p | arquivo raw |
|---|---|---|---|---|---|
| inicial (contexto genérico, evaluator estrito) | 24/40 (60.0%) | 26/40 (65.0%) | −5.0 pp | 1.0 | `*_30bfd1ed.jsonl` |
| pós-D-005 | 34/40 (85.0%) | 29/40 (72.5%) | +12.5 pp | 0.18 | `*_7f82b1f5.jsonl` |
| pós-D-006 | 35/40 (87.5%) | 26/40 (65.0%) | **+22.5 pp** | **0.0039** | `*_243a0e26.jsonl` |
| réplica Qwen 27B (pós-D-007) | 34/40 (85.0%) | 22/40 (55.0%) | **+30.0 pp** | **0.00049** | `*_06a0ccb0.jsonl` |

Dois achados centrais do TCC:

1. **Design importa**: a qualidade do contexto semântico e a consistência do banco de perguntas determinam se o efeito aparece. Mal projetados, parece não haver diferença (Δ = −5 pp inicial, não significativo); projetados cuidadosamente, o efeito é significativo mesmo com n=40.
2. **Efeito replica em modelo diferente**: direção, magnitude e significância se preservam ao trocar `gpt-oss-120b` por `qwen3.8-27b`. A condição semântica mantém ~85% de acurácia em ambos; a técnica degrada com o modelo menor (65% → 55%). Isso sugere que **modelos menos capazes se beneficiam ainda mais do contexto semântico**.

## Próximos passos (escrita do TCC)

1. Escrever seção de Resultados citando `artifacts/reports/results_final.md`, `artifacts/processed/accuracy.csv`, `artifacts/processed/by_category.csv`, `artifacts/processed/error_types.csv`.
2. Narrar a iteração metodológica da D-005 como contribuição do próprio TCC: "contexto semântico mal projetado pode degradar o desempenho; corrigido, aparece 12.5 pp acima do técnico — resultado sugestivo (p=0.18) a ser confirmado com n maior".
3. Discutir limitações: n=40 limita poder estatístico (p=0.18 não atinge α=0.05); modelo único (`gpt-oss-120b`); snapshot único da base; evaluator por igualdade de rows ainda penaliza respostas com colunas descritivas extras — ver audit em `artifacts/processed/_failures_audit.txt`.
4. Discutir trade-off de latência: semantic ~3.7x mais lento por conta do prompt maior — custo real de produção que vale mencionar.

## Observações para versionamento

- `.env`, planilhas de origem (`.xlsx`), e resultados brutos em `artifacts/raw/` não vão para o GitHub.
- CSVs/reportes agregados em `artifacts/processed/` e `artifacts/reports/` são versionáveis — não contêm valores de linhas.
- Decisões metodológicas e de privacidade estão em `docs/decisions.md`.
