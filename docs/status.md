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

Relatório: `artifacts/reports/results_final_qwen3-27b-tiers.md` (run `07a25f55`). Desenho progressivamente aditivo (technical ⊂ catalog ⊂ semantic), análogo ao benchmark da comunidade Databricks ("Which context improves Genie accuracy most?", 40% → 47% → 97%).

- **technical** (DDL puro): 23/40 = 57.50% (CI95 42.2–72.8%)
- **catalog** (DDL + descrições por tabela e coluna): 24/40 = 60.00% (CI95 44.8–75.2%)
- **semantic** (catalog + regras de grão + temporais + referenciais + estilo + sinônimos): **35/40 = 87.50%** (CI95 77.3–97.7%)

McNemar pareado (p bruto / p ajustado por Holm na família de 3 comparações):

- technical vs catalog: 1:2 discordantes, **p = 1.0 / 1.0** — adicionar apenas comentários de catálogo não muda acurácia de forma significativa.
- catalog vs semantic: 0:11 discordantes, **p = 0.00098 / 0.0020** — adicionar a camada semântica estruturada é o que produz o salto.
- technical vs semantic: 0:12 discordantes, **p = 0.00049 / 0.0015** — gap total significativo após ajuste.

Latência mediana: 2.9 s → 7.7 s → 14.8 s (todas as comparações pareadas significativas, p < 10⁻⁸).

Replicação do shape do benchmark Databricks com modelo open-source e sem Unity Catalog proprietário.

Correção (16/11/2026): a primeira versão deste relatório mostrava n=39 porque foi gerada antes do fim da run `07a25f55` — o último registro (Q040, condição technical) foi gravado às 19:36:35 UTC e o relatório foi commitado às 19:37:27 UTC. A explicação anterior ("questão descartada por falha de execução") estava errada: as 40 perguntas têm as três condições completas, e falhas de execução (Q027 em technical e catalog) contam como `correct=False`. Relatório e CSVs regenerados a partir do raw completo com `scripts/analyze_results.py --run 07a25f55 --suffix qwen3-27b-tiers`.

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

### Ablação de 3 tiers (D-008): `openai/gpt-oss-120b`

- **technical** (DDL puro): 25/40 = 62.50% (CI95 47.5–77.5%)
- **catalog** (DDL + descrições por tabela e coluna): 28/40 = 70.00% (CI95 55.8–84.2%)
- **semantic** (catalog + regras + estilo): **33/40 = 82.50%** (CI95 70.7–94.3%)

McNemar pareado (p bruto / p ajustado por Holm na família de 3 comparações):

- technical vs catalog: 0:3 discordantes, **p = 0.25 / 0.36** — direção correta, não significativo com n=40.
- catalog vs semantic: 2:7 discordantes, **p = 0.18 / 0.36** — direção correta, não significativo.
- technical vs semantic: 1:9 discordantes, **p = 0.0215 / 0.064** — significativo a α=0.05 só sem ajuste; após Holm, não significativo.

Decisão de 16/11/2026: o TCC reporta p bruto e p ajustado por Holm lado a lado, e a significância é decidida pelo ajustado. `scripts/analyze_results.py` passou a gravar a coluna `p_holm` em `mcnemar_pairs_*.csv` e nos relatórios.

Latência mediana: 1.4 s → 1.4 s → 7.9 s. O catálogo praticamente não altera a mediana de latência (1400 ms vs 1394 ms; Wilcoxon p = 0.048, diferença estatística sem relevância prática); a camada semântica adiciona ~5,6× de latência.

### Comparação entre modelos (D-008)

| tier | gpt-oss-120b | qwen3.8-27b | Databricks Genie |
|---|---|---|---|
| technical | 62.5% | 57.5% | 40% |
| catalog | 70.0% (+7.5pp) | 60.0% (+2.5pp) | 47% (+7pp) |
| semantic | 82.5% (+12.5pp) | 87.5% (+27.5pp) | 97% (+50pp) |

Padrão replicado nos três conjuntos: três tiers, acurácia monotônica crescente, salto maior no último tier. O ganho absoluto do catálogo varia com o modelo (maior em gpt-oss-120b, menor em qwen3.8-27b), mas o ganho da camada semântica sobre o catálogo é consistente e significativo no agregado.

### Histórico de iterações metodológicas (modelo principal)

| iteração | semantic | technical | Δ | McNemar p | arquivo raw |
|---|---|---|---|---|---|
| inicial (contexto genérico, evaluator estrito) | 24/40 (60.0%) | 26/40 (65.0%) | −5.0 pp | 0.625 | `*_30bfd1ed.jsonl` |
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
