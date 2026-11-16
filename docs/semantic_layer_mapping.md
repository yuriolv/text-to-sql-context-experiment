# Mapa conceitual: `semantic_context.yaml` × tooling industrial

Cada seção do nosso `semantic_context.yaml` tem um análogo direto em pelo menos três stacks de semantic layer usadas em produção: **dbt Semantic Layer**, **Databricks Unity Catalog**, **LookML** e **Cube**. A tabela abaixo mostra o mapeamento conceito a conceito; usada no TCC, demonstra que o artefato que estudamos **não é um formato ad-hoc** — é um recorte mínimo e aberto do que essas plataformas proprietárias definem.

## Tabela de equivalências

| Nossa seção YAML | dbt Semantic Layer | Unity Catalog (Databricks) | LookML (Looker) | Cube |
|---|---|---|---|---|
| `domain` / `privacy` (cabeçalho) | `description:` em `semantic_models` | `COMMENT ON SCHEMA` + tags de catálogo | `label:` + `description:` do model | `title` + `description` do cube |
| `money_fields.<coluna>` (descrição por campo monetário) | `measures:` com `expr` | `COMMENT ON COLUMN` + metric views | `measure:` com `sql:` | `measures: {sql: ...}` |
| `count_fields.<coluna>` (descrição por campo de contagem) | `measures:` com `agg: count` | `COMMENT ON COLUMN` | `measure:` com `type: count` | `measures: {type: count}` |
| `grain_rules` (grão de pedido vs item) | `entities:` + `semantic_models` com `primary_key` | metric views com `MEASURE()` por tabela | `view:` com `sql_table_name:` + `primary_key:` | `cubes:` separados por grão |
| `temporal_rules` (qual coluna de data usar) | `dimensions:` com `type: time` + `type_params` | `time_dimension` em metric views | `dimension_group:` com `type: time` | `dimensions: {type: time}` |
| `referential_rules` (JOIN vs IS NOT NULL em FK órfã) | `entities:` com `type: foreign` + `join` em metrics | lineage + FK constraints no Unity Catalog | `join:` com `relationship:` e `sql_on:` | `joins:` com `relationship` + `sql` |
| `synonyms` (vocabulário pt-BR → tabela/coluna) | `label:` + `aliases:` (parcial) | tags + glossário no catálogo | `label:` + `description:` por campo | nativo (`title`, aliases via meta) |
| `response_style` (não acrescentar colunas, não castar) | implícito no compilador MetricFlow | implícito no SQL gerado pelo catálogo | implícito na API do Looker | implícito na API do Cube |

## Observações importantes para o TCC

**1. `response_style` não tem análogo direto nessas plataformas.** Nas quatro, a disciplina de output é resolvida por **compilação**: você pede uma métrica, o compilador gera um SQL determinístico que não tem "colunas extras". No nosso caso, como o agente gera SQL livremente, a disciplina precisa ser codificada como instrução no contexto. Isso é uma consequência do **runtime** (LLM free-form vs semantic-layer-API), não do artefato semântico. Vale mencionar como limitação do nosso setup e como evidência de que a camada semântica textual é o piso mais barato — não o teto.

**2. `referential_rules` é mais explícito no nosso YAML do que nas outras plataformas.** Em dbt/Unity/LookML/Cube, o relacionamento é declarado (`entities`, `join`, `relationship`), e o compilador gera o JOIN. Nossa regra em prosa (`"Para 'quantos X estão associados a Y existente', use JOIN"`) é necessária porque o agente LLM é quem escreve o SQL. Essa é a mesma informação declarativa, só que renderizada como instrução.

**3. `grain_rules` mapeia ao conceito fundamental da camada semântica.** dbt chama de `entity`, Cube chama de `cube`, LookML chama de `view`, Unity Catalog chama de `metric view`. Todos codificam a ideia de que **uma tabela tem um grão** e agregações devem respeitar esse grão. O nosso `grain_rules` é a formulação prosódica dessa ideia.

**4. Nenhuma das quatro plataformas "escapa" do prompt engineering na ponta do agente.** Quando qualquer agente LLM consome dbt Semantic Layer, Unity Catalog metric views, LookML `view` ou Cube `cube`, o metadado inevitavelmente **chega como texto no prompt do modelo**. A diferença está em onde o metadado dorme em repouso (arquivo YAML local vs linha no catálogo vs objeto em cache) e em quem compila (humano vs MetricFlow vs Databricks Data Intelligence vs Cube Query Engine). O conteúdo e a utilidade para o agente são equivalentes.

## Mínimo irredutível: o que uma camada semântica precisa carregar

Destilando o que todas essas ferramentas e o nosso YAML têm em comum:

1. **Definições por campo** — o que cada coluna monetária/contagem/dimensão significa em linguagem de negócio.
2. **Grão** — a chave de cada tabela e qual nível de agregação ela representa.
3. **Dimensões temporais** — qual coluna de data é "a" data da métrica.
4. **Relacionamentos** — como combinar tabelas e o que fazer com integridade referencial imperfeita.
5. **Sinônimos** — ponte do vocabulário do usuário para o schema físico.

Essas cinco categorias são o **irredutível conceitual** da camada semântica. Elas aparecem em todas as plataformas industriais e no nosso YAML. Quando falamos "a camada semântica importa pra text-to-SQL agentic", é dessas cinco categorias que estamos falando — não de um formato específico, não de uma ferramenta específica, não de "prompt engineering".

## Implicações para o posicionamento do TCC

O trabalho pode ser lido como um **estudo de ablação do piso dessa camada semântica**: ao invés de usar dbt ou Unity Catalog, usamos o formato mais barato possível (um YAML em disco injetado no prompt) e medimos o efeito empírico. O fato de o resultado replicar o shape do benchmark da Databricks (40% → 47% → 97%, análogo aos nossos 62% → 70% → 83% em gpt-oss e 59% → 62% → 87% em qwen) é evidência de que:

- A **categoria de informação** é o que importa, não o formato de autoria ou o tooling de runtime.
- A camada semântica é um conceito transferível entre stacks, não um lock-in de plataforma.
- Um TCC pode fazer essa validação **sem licença paga**, com dois LLMs open-source e cinco páginas de YAML.
