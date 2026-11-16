# Taxonomia de erros

Classificação sistemática das 16 perguntas da coleta final (`openai/gpt-oss-120b`, 3-tier, run `22e3f8ce`) em que alguma das três condições produziu `wrong_result` ou `database`. Classificação manual a partir de `artifacts/processed/_failures_audit_tiers_gpt-oss.txt`. Para cada tipo de erro listamos: diagnóstico, perguntas afetadas, em quais tiers aparece, e qual seção do YAML semântico endereça (ou não endereça).

## Resumo em uma tabela

| Tipo de erro | n perguntas | tier mínimo que resolve | seção endereçante | representativas |
|---|---|---|---|---|
| **A. Escolha de coluna (ambiguidade lexical)** | 2 | catalog | `money_fields` / `count_fields` | Q005, Q032 |
| **B. FK órfã (JOIN vs IS NOT NULL)** | 4 | semantic | `referential_rules` | Q011, Q013, Q014, Q015 |
| **C. Estilo verboso (colunas descritivas extras)** | 5 | semantic | `response_style` | Q013, Q018, Q020, Q037, Q038 |
| **D. Tipo e formato temporal** | 2 | não resolve | (ambiguidade do gold) | Q022, Q027 |
| **E. "Percentual" (fração × 100)** | 1 | não resolve | (ambiguidade linguística) | Q035 |
| **F. Ambiguidade genuína do enunciado** | 2 | não resolve | — | Q019, Q040 |
| **G. Interpretação de "média"** | 1 | não resolve | (gold hardcoded) | Q039 |

Totais podem ultrapassar 16 porque uma mesma pergunta pode ser afetada por mais de um tipo (Q013 é B + C).

## Detalhes por tipo

### A. Escolha de coluna por ambiguidade lexical

A pergunta usa um termo em pt-BR que mapeia para mais de uma coluna possível; o modelo escolhe a errada sem contexto.

**Perguntas:**
- Q005 "média de **quantidade de itens** informada" → `orders.item_count` (certo) vs `SUM(order_items.quantity) GROUP BY order_id` (errado)
- Q032 "faturamento no **grão de item**" → `SUM(order_items.total_amount)` (certo) vs breakdown por produto (errado)

**Comportamento por tier:**
- `technical`: erra. Sem descrição, escolhe a coluna com nome mais familiar ao modelo.
- `catalog`: acerta. A descrição `item_count — quantidade de itens informada no cabeçalho do pedido; distinta de COUNT(*)...` em `catalog_context.sql` resolve em uma linha. Idem `total_amount — valor do item (quantity × unit_price) no grão de item`.
- `semantic`: acerta.

**Implicação:** este é o tipo de erro que **só a camada de catálogo já consertaria**, consistente com o salto technical→catalog de +7.5 pp em gpt-oss. Para erros tipo A, Unity Catalog comments já bastam.

### B. FK órfã (JOIN vs IS NOT NULL)

A pergunta usa "X associado a Y" e o modelo precisa decidir entre contar o campo preenchido (`WHERE y_id IS NOT NULL`) ou contar associações a linhas existentes na tabela referenciada (`JOIN Y`). Por D-004, a base tem referências órfãs, então as duas formulações divergem.

**Perguntas:**
- Q011 "pedidos têm cliente associado" (gold: JOIN; diferença: 10931 vs 10375)
- Q013 "clientes associados a representante" (gold: JOIN; diferença: 2644 vs 2362)
- Q014 "produtos têm subgrupo associado" (gold: JOIN; diferença: 1922 vs 1554)
- Q015 "subgrupos associados a grupos" (gold: JOIN; diferença: 168 vs 167)

**Comportamento por tier:**
- `technical`: erra consistentemente — assume IS NOT NULL.
- `catalog`: ainda erra na maioria dos casos. A descrição `representative_id FK -> representatives` **não diz que a FK pode ser órfã**.
- `semantic`: acerta. A regra `"Para 'quantos X estão associados a Y existente', use JOIN"` em `referential_rules` é o que resolve.

**Implicação:** esta classe é o principal driver do salto catalog→semantic. Não cabe em descrição de coluna porque é uma regra sobre **como o schema deve ser consultado em presença de impureza nos dados**, não uma definição do que a coluna significa.

### C. Estilo verboso (colunas descritivas extras)

A pergunta pede contagem/agregação; o modelo adiciona colunas de nome (`.name`, `.representative_name`, `.product_name`) ao `GROUP BY`. SQL semanticamente correto, mas resultado estrutural diferente do gold por hash.

**Perguntas:**
- Q013 (também em B), Q018, Q020, Q037, Q038

**Comportamento por tier:**
- `technical` e `catalog`: ambos erram do mesmo jeito. O catálogo inclusive **incentiva** o padrão ao descrever cada tabela ("representatives: representantes de vendas" sugere trazer nomes).
- `semantic`: acerta. A regra `"Devolva apenas as colunas pedidas: a chave de agrupamento e as agregações. Não acrescente colunas descritivas (como nome) se a pergunta não pediu"` em `response_style` é o que disciplina.

**Implicação:** segundo maior driver do salto catalog→semantic. É puramente uma regra de **output**, independente do conteúdo do schema.

### D. Tipo e formato temporal

O gold usa um cast específico (`::date`, `::int`) que o modelo não reproduz exatamente. O evaluator relaxado (D-005) absorve `int ↔ Decimal` e `datetime 00:00:00 UTC ↔ date`, mas não cobre `text 'YYYY-MM'` vs `date`, ou `TIMESTAMP - TIMESTAMP` vs `DATE - DATE`.

**Perguntas:**
- Q022 "pedidos por mês": gold `DATE_TRUNC('month', issued_at)::date` vs modelo `TO_CHAR(..., 'YYYY-MM')` ou duas colunas (year, month).
- Q027 "duração média em dias": gold `AVG(expected_delivery_date - issued_at)` vs modelo com `EXTRACT(EPOCH FROM ...)` (quebra em PostgreSQL com DATE - DATE porque devolve int, não interval).

**Comportamento por tier:**
- Nenhum tier resolve consistentemente. É problema de **convenção de tipo** que o YAML não codifica (talvez devesse, como trabalho futuro).

**Implicação:** erros desta classe são distribuídos entre tiers e não produzem gap entre eles. Contribuem para o teto do estudo (acurácia máxima atingível com n=40).

### E. "Percentual" (fração × 100)

Em pt-BR, "percentual" quase sempre significa "número vezes 100 com %"; mas o gold `SUM(d) / SUM(g)` devolve a fração (0.0743). O modelo multiplica por 100 (7.43) e erra tecnicamente.

**Perguntas:**
- Q035.

**Comportamento por tier:**
- Todos os três erram. É um descasamento de convenção entre o gold (SQL literal) e a linguagem natural.

**Implicação:** potencial correção futura do gold em uma próxima iteração. Candidato a nota de limitação no TCC.

### F. Ambiguidade genuína do enunciado

O enunciado em pt-BR tem duas interpretações defensáveis; o modelo escolhe uma, o gold escolhe outra, nenhum tier reconcilia.

**Perguntas:**
- Q019 "quantidade de itens por grupo": gold conta linhas (`COUNT(*)`), modelo soma quantities (`SUM(oi.quantity)`). Ambos são leituras válidas de "quantidade de itens".
- Q040 "diferença entre valor bruto e desconto, somada por pedido": gold agrega (`SUM(...)`), modelo devolve por linha. A frase "somada por pedido" é ambígua — pode ser "uma soma, pedido a pedido" (modelo) ou "o total somado" (gold).

**Implicação:** candidatos a reescrita do enunciado em uma próxima iteração. Não é falha de contexto, é falha de especificação.

### G. Interpretação de "média"

**Perguntas:**
- Q039 "média de valor realizado nas metas por representante": gold `AVG(achieved_amount) GROUP BY representative_id`; technical computa "média das médias" (CTE com AVG por rep, depois AVG do AVG).

**Comportamento por tier:**
- `catalog` e `semantic`: acertam.
- `technical`: erra. Pode ser visto como caso Especial do tipo A (`achieved_amount — valor realizado...` em catalog_context.sql explica o campo).

**Implicação:** reforça o padrão A — descrição de coluna cura.

## Como isso informa o texto do TCC

A taxonomia justifica numericamente a tese central: **a camada semântica resolve classes de erro que o catálogo sozinho não resolve.**

- Tipo A (6 pontos de ganho potenciais): catálogo basta → salto technical→catalog
- Tipo B + Tipo C (9 pontos de ganho potenciais): só semantic → salto catalog→semantic
- Tipos D, E, F, G (4-5 pontos de teto): não endereçados por nenhum tier com o YAML atual → é o resíduo da acurácia

Esse decomposição numérica deveria aparecer como figura ou tabela na seção de resultados. Reforça que o ganho não é efeito agregado misterioso — é a soma de classes distintas e nomeáveis.
