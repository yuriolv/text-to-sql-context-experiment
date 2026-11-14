# Briefing para o agente redator do TCC

Documento único de contexto para quem for escrever o TCC. Consolida o essencial de `README.md`, `docs/status.md` e `docs/decisions.md`; os três continuam sendo fonte autoritativa para detalhes.

## 1. Pergunta do experimento

Em um agente Text-to-SQL baseado em LLM, **enriquecer o contexto técnico (schema puro) com uma camada semântica (glossário, regras de grão, regras temporais e referenciais, estilo de resposta) melhora a correctness das consultas geradas?**

A hipótese nula é "não há diferença entre as duas condições". A alternativa é bilateral — o estudo foi projetado para detectar tanto melhora quanto piora.

## 2. Objeto de estudo

- **Base**: `commercial`, 11 planilhas XLSX comerciais descaracterizadas e autorizadas para uso acadêmico local (D-001), transformadas em esquema PostgreSQL sem enforcement de FK (D-004). Volume: 10.931 pedidos, 246.737 itens, intervalo 2016-01-18 → 2026-02-26.
- **Agente**: Text-to-SQL direto, prompt único (system + schema + pergunta), sem few-shot, sem ferramentas. Até 3 tentativas por pergunta se o SQL falhar na validação ou na execução; feedback técnico é devolvido ao modelo entre tentativas.
- **Modelos** (ambos via Groq free tier, OpenAI-compatível):
  - `openai/gpt-oss-120b` (OpenAI, 120B) — principal
  - `qwen/qwen3.8-27b` (Alibaba, 27B) — réplica para validade externa (D-007)
- **Parâmetros fixos**: `temperature=0`, `max_tokens=800`, seed registrado por request.
- **Perguntas**: 40 perguntas da coleta final em 4 categorias (`filters_aggregations`, `relationships`, `temporal`, `business_rules`); 10 perguntas separadas para piloto. Em `data/datasets/commercial/questions_final.jsonl` e `questions_pilot.jsonl`. Cada pergunta traz gold SQL e tolerância numérica.

## 3. Condições comparadas

Pareamento perfeito: cada pergunta é apresentada em **três condições progressivamente aditivas** na mesma rodada; a ordem é contrabalanceada por 6 permutações rotacionadas (D-002 + D-008).

- **Técnica (`technical`)**: DDL textualizado em `data/datasets/commercial/technical_context.sql`. Descreve tabelas, colunas, PKs e FKs textualmente, sem descrição de campo. Análogo a "tables only" no benchmark da comunidade Databricks.
- **Catálogo (`catalog`)**: DDL + descrições por tabela e por coluna para campos não triviais, em `data/datasets/commercial/catalog_context.sql`. Análogo direto a `COMMENT ON TABLE`/`COMMENT ON COLUMN` do Unity Catalog ou "tables + UC descriptions" no benchmark citado.
- **Semântica (`semantic`)**: catálogo + conteúdo de `semantic_context.yaml` (regras de grão pedido↔item, regras temporais, regras referenciais para FKs órfãs de D-004, sinônimos pt-BR, estilo de resposta). Análogo a "+ metric views + instructions" no benchmark citado.

O desenho de três tiers aditivos permite isolar o salto "catálogo → semântico" do salto "técnico → catálogo".

## 4. Trajetória metodológica (D-001 a D-007)

Resumo das 7 decisões (texto integral em `docs/decisions.md`):

| ID | Decisão | Motivo |
|---|---|---|
| D-001 | Fonte experimental `commercial`; `financeiro` excluído | Autorização específica para a primeira; privacidade na segunda. |
| D-002 | Pareamento + contrabalanceamento + 1 repetição no final | `temperature=0` torna repetições redundantes; poder estatístico vem das 40 perguntas pareadas. |
| D-003 | Nenhum dado de linha enviado a provedor externo | Privacidade. |
| D-004 | `schema.sql` sem `REFERENCES` | Dados reais têm FKs órfãs; preservar a fonte como autorizada. |
| D-005 | Reescrever `semantic_context.yaml` + relaxar evaluator | Rodada pré-D-005 apontou glossário mal projetado (sinônimo genérico `valor_pedido`) e avaliador penalizando equivalências de tipo (`int` vs `Decimal`, `date` vs `datetime` à meia-noite). |
| D-006 | Padronizar gold SQL em perguntas "associado" | Gold era internamente inconsistente (4 perguntas com `JOIN`, 3 com `IS NOT NULL`); escolha estrutural pela maioria pré-existente (`JOIN`). |
| D-007 | Replicar em `qwen/qwen3.8-27b` | Testar validade externa — efeito depende do modelo? |
| D-008 | Adicionar terceiro tier `catalog` | Alinhar ao benchmark Databricks Genie (40→47→97): separar o salto DDL→comentários de catálogo do salto catálogo→camada semântica. |

## 5. Resultados

### Modelo principal `openai/gpt-oss-120b`

- semantic: **35/40 = 87.5%** (CI95 77.3–97.7)
- technical: 26/40 = 65.0% (CI95 50.2–79.8)
- Δ = **+22.5 pp**
- McNemar pareado: 9 pares discordantes, 9:0 a favor de semantic, **p = 0.0039**
- Latência Wilcoxon: p ≈ 10⁻⁴; semantic mediana 3438 ms vs technical 1488 ms

### Réplica `qwen/qwen3.8-27b`

- semantic: 34/40 = 85.0% (CI95 73.9–96.1)
- technical: 22/40 = 55.0% (CI95 39.6–70.4)
- Δ = **+30.0 pp**
- McNemar pareado: 12 pares discordantes, 12:0 a favor de semantic, **p = 0.00049**
- Latência Wilcoxon: p ≈ 10⁻¹¹; semantic mediana 10.3 s vs technical 3.2 s

### Evolução por iteração (apenas modelo principal)

| iteração | semantic | technical | Δ | McNemar p |
|---|---|---|---|---|
| inicial (contexto genérico, evaluator estrito) | 60.0% | 65.0% | −5.0 pp | 1.0 |
| pós-D-005 | 85.0% | 72.5% | +12.5 pp | 0.18 |
| pós-D-006 | **87.5%** | 65.0% | **+22.5 pp** | **0.0039** |

Raw files de cada iteração preservados em `artifacts/raw/` para auditoria.

## 6. Achados a serem defendidos no texto

1. **Design importa**: a qualidade do contexto semântico e a consistência estrutural do banco de perguntas determinam fortemente se o efeito aparece. Na primeira rodada (contexto mal projetado, gold inconsistente), não haveria diferença estatística — ou haveria diferença negativa aparente. Com design iterado e documentado, o efeito é significativo mesmo com n=40.
2. **Replicação externa**: direção, magnitude e significância se preservam ao trocar `gpt-oss-120b` por `qwen3.8-27b`. A condição semântica mantém ~85% em ambos; a técnica degrada no modelo menor (65% → 55%).
3. **Efeito compensatório em modelos menos capazes**: o gap aumenta (não diminui) com modelo menor. Interpretação: o contexto semântico compensa parte da capacidade bruta do modelo — modelo menor com contexto bom se aproxima de modelo grande com contexto técnico apenas.
4. **Trade-off de latência**: semantic é 2–3x mais lento em ambos os modelos (prompt maior). Custo real de produção que merece menção.

## 7. Limitações a foreground no texto

- **n=40**. Baixo poder para detectar efeitos pequenos. Com 9 e 12 pares discordantes totalmente alinhados à semântica, atingiu-se p < 0.01 e p < 0.001, mas um efeito menor em outro contexto poderia passar despercebido.
- **Dois modelos**. Replicação externa estabelecida, mas não exaustiva. Modelos muito grandes (frontier proprietários) ou muito pequenos (<10B) não foram testados.
- **Snapshot único da base**. Mudanças na base poderiam alterar a dificuldade das perguntas. A seleção foi fixa.
- **Iteração metodológica sobre dados vistos**. D-005 e D-006 foram decididos após observar erros do piloto/primeira final. A mitigação é que ambas as iterações usaram critérios **estruturais** (reescrita por tabela/categoria, padronização pela maioria linguística já presente), não por pergunta individual — mas a possibilidade de viés de pesquisador deve ser admitida.
- **Avaliador por igualdade de resultado**. O relaxamento de D-005 cobre tipos; ainda penaliza respostas com colunas descritivas extras semanticamente corretas. É uma fronteira conservadora — qualquer melhora medida é piso, não teto.
- **Pergunta ambígua em pt-BR**. Q019 ("quantidade de itens"), Q035 ("percentual") e Q040 ("diferença… somada") têm ambiguidade linguística genuína; falham nos dois modelos e em ambas as condições.

## 8. Onde encontrar o quê

- Protocolo e perguntas congeladas (conteúdo): `data/datasets/commercial/`
- Decisões metodológicas (D-001 a D-007): `docs/decisions.md`
- Estado e resultados agregados: `docs/status.md`
- Relatórios estatísticos por modelo (markdown com tabelas): `artifacts/reports/results_final_gpt-oss-120b.md`, `artifacts/reports/results_final_qwen3-27b.md`
- CSVs por modelo (prontos pra tabular no TCC): `artifacts/processed/accuracy_<modelo>.csv`, `by_category_<modelo>.csv`, `error_types_<modelo>.csv`
- Registros brutos por execução (uma linha JSON por tentativa): `artifacts/raw/*.jsonl`
- Auditoria qualitativa das falhas (classificação pergunta a pergunta, com SQL gerado e resultado real): `artifacts/processed/_failures_audit.txt` (pré-D-005) e `_failures_audit_v2.txt` (pós-D-005)
- Código do experimento (agente, runner, evaluator, provedor LLM, controles): `src/tccsql/`
- Scripts operacionais: `scripts/`

## 9. Notas para o redator

- O texto deve ser em português, formato de TCC/monografia (a norma específica — ABNT, template da faculdade — não está neste repositório e precisa ser suprida separadamente).
- Revisão bibliográfica / trabalhos relacionados **não** estão no repositório. O redator vai precisar levantar literatura sobre Text-to-SQL, prompt engineering, semantic layer, benchmarks (Spider, BIRD) por conta própria.
- Nome do orientador, banca, data da defesa, elementos pré-textuais (resumo, abstract, lista de figuras) não estão aqui.
- Todas as afirmações numéricas no texto devem ser rastreáveis a um arquivo em `artifacts/`. Se o redator não encontrar a fonte, pergunta antes de inventar.
