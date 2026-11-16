# Exemplos qualitativos (coleta final, `openai/gpt-oss-120b`)

Cinco perguntas escolhidas da coleta final para ilustrar, com SQL e resultados reais, o que cada tier de contexto muda. Todos os registros vêm de `artifacts/raw/20261114T134134_commercial_final_22e3f8ce.jsonl` (gpt-oss-120b, 3-tier, pós-D-008). Os resultados foram re-executados no Postgres via `scripts/_audit_failures.py` com `AUDIT_RUN_ID=22e3f8ce`.

A primeira linha de cada exemplo descreve o **padrão** do caso: qual tier conserta o erro, e por qual seção do artefato semântico.

---

## Q005 — "Qual é a média de quantidade de itens informada nos pedidos?"

**Padrão:** catalog consegue, semantic também. A descrição por coluna já basta.

Gold SQL (padronizado em D-006):
```sql
SELECT AVG(item_count) FROM orders
```
Gold result: `9.9597`

**technical** — ❌
```sql
WITH order_qty AS (
  SELECT oi.order_id, SUM(oi.quantity) AS total_qty
  FROM order_items AS oi
  GROUP BY oi.order_id
)
SELECT AVG(total_qty) AS avg_quantity_per_order FROM order_qty
```
Resultado: `455.64`. O modelo não sabia que `orders.item_count` existe e assumiu que "quantidade de itens" tinha que ser somada em `order_items`.

**catalog** — ✅
```sql
SELECT AVG(item_count) AS average_item_count FROM orders
```
A linha `item_count — quantidade de itens informada no cabeçalho do pedido; distinta de COUNT(*) sobre order_items` em `catalog_context.sql` foi suficiente para o modelo escolher a coluna certa.

**semantic** — ✅
```sql
SELECT AVG(item_count) FROM orders
```
Idem.

---

## Q011 — "Quantos pedidos têm cliente associado?"

**Padrão:** só semantic acerta. O catálogo não distingue FK órfã de FK informada; a regra referencial precisa estar explícita.

Gold SQL (padronizado em D-006):
```sql
SELECT COUNT(*) FROM orders o JOIN customers c ON c.customer_id = o.customer_id
```
Gold result: `10375`

**technical** — ❌
```sql
SELECT COUNT(*) AS pedidos_com_cliente FROM orders WHERE customer_id IS NOT NULL
```
Resultado: `10931`. Diferença de 556 linhas — pedidos com `customer_id` preenchido mas referenciando cliente inexistente (FK órfã, documentada em D-004).

**catalog** — ❌
```sql
SELECT COUNT(*) AS orders_with_customer FROM orders WHERE customer_id IS NOT NULL
```
Mesmo erro. Comentário de coluna não resolve ambiguidade: "associado a Y" pode querer dizer "campo preenchido" ou "linkado a Y existente".

**semantic** — ✅
```sql
SELECT COUNT(*) AS total_orders_with_customer
FROM orders AS o
JOIN customers AS c ON o.customer_id = c.customer_id
```
A regra em `semantic_context.yaml::referential_rules` — "Para 'quantos X estão associados a Y existente', use JOIN com a tabela Y (exclui referências órfãs)" — é o que distingue os dois tiers. Não é uma informação de catálogo, é uma regra sobre como interpretar a pergunta.

---

## Q013 — "Quantos clientes estão associados a um representante?"

**Padrão:** technical e catalog erram de formas diferentes; só semantic combina referência correta com estilo de resposta correto.

Gold SQL:
```sql
SELECT COUNT(*) FROM customers c JOIN representatives r ON r.representative_id = c.representative_id
```
Gold result: `2362`

**technical** — ❌
```sql
SELECT COUNT(*) AS total_customers FROM customers WHERE representative_id IS NOT NULL
```
Resultado: `2644`. Mesmo erro de FK órfã do Q011.

**catalog** — ❌ (de outro jeito)
```sql
SELECT r.representative_id, r.name, COUNT(c.customer_id) AS customer_count
FROM representatives AS r
LEFT JOIN customers AS c ON c.representative_id = r.representative_id
GROUP BY r.representative_id, r.name
ORDER BY customer_count DESC
```
O catálogo descreve o que cada tabela é e incentiva o modelo a fazer o JOIN, mas sem regra de estilo ele acrescenta `name`, `GROUP BY`, `ORDER BY` — devolve um ranking em vez de uma contagem. Resultado estruturalmente diferente do gold.

**semantic** — ✅
```sql
SELECT COUNT(*) AS total_customers
FROM customers AS c
JOIN representatives AS r ON c.representative_id = r.representative_id
```
A regra de `response_style` ("devolva apenas as colunas pedidas: a chave de agrupamento e as agregações") é o que mantém a resposta concisa e correta. Só com a parte referencial do catálogo, sem o `response_style`, o modelo faz over-engineering.

---

## Q032 — "Qual é o faturamento total no grão de item?"

**Padrão:** a descrição por coluna que menciona o grão basta; não precisa das regras adicionais.

Gold SQL:
```sql
SELECT SUM(total_amount) FROM order_items
```
Gold result: `300415755.947`

**technical** — ❌
```sql
SELECT oi.product_id, p.name AS product_name, SUM(oi.total_amount) AS total_revenue
FROM order_items AS oi
JOIN products AS p ON p.product_id = oi.product_id
GROUP BY oi.product_id, p.name
ORDER BY total_revenue DESC
```
Resultado: linhas por produto, não um escalar. "Grão de item" foi lido como "detalhado por item (produto)" em vez de "no nível de linha de `order_items`".

**catalog** — ✅
```sql
SELECT SUM(total_amount) AS total_faturamento_item FROM order_items
```
O comentário da coluna em `catalog_context.sql` — "Valor do item (quantity × unit_price) no grão de item" — resolveu a ambiguidade. O catálogo é suficiente quando a disambiguação cabe em uma descrição de campo.

**semantic** — ✅
```sql
SELECT SUM(order_items.total_amount) AS total_faturamento_item FROM order_items
```
Idem, mas com `order_items.` qualificado.

---

## Q038 — "Qual é o valor total de pedidos por representante?"

**Padrão:** technical e catalog erram pelo mesmo motivo estrutural (JOIN com `representatives` para pegar `name`); semantic é parcimonioso graças ao `response_style`.

Gold SQL:
```sql
SELECT representative_id, SUM(total_amount) FROM orders GROUP BY representative_id
```
Gold result (primeiros 5): `(54, 11022.19), (68, 23454.09), (4, 299852.24), (34, 34853.17), (51, 19624.72)`

**technical** — ❌
```sql
SELECT r.representative_id, r.name, SUM(o.total_amount) AS total_order_value
FROM orders AS o
JOIN representatives AS r ON o.representative_id = r.representative_id
GROUP BY r.representative_id, r.name
```
INNER JOIN com `representatives` exclui orders com `representative_id` órfão (as linhas com IDs como 54 que não existem na tabela de representatives). Também acrescenta coluna `name`.

**catalog** — ❌
```sql
SELECT r.representative_id, r.name, SUM(o.total_amount) AS total_order_value
FROM orders AS o
JOIN representatives AS r ON o.representative_id = r.representative_id
GROUP BY r.representative_id, r.name
```
Praticamente idêntico. O catálogo descreve o que cada tabela representa, mas isso incentiva o modelo a *usar* `representatives` e trazer `name`.

**semantic** — ✅
```sql
SELECT r.representative_id, SUM(o.total_amount) AS total_order_value
FROM orders AS o
JOIN representatives AS r ON o.representative_id = r.representative_id
GROUP BY r.representative_id
```
Ainda faz o JOIN (pelas regras referenciais), mas sem a coluna `name` extra. Esse exemplo mostra que o `response_style` do tier semantic **compensa** a tendência do tier catalog de inflar a resposta.

---

## Padrão geral extraído dos cinco exemplos

| Caso | O que resolve | Qual seção do YAML? |
|---|---|---|
| Q005 | Escolher a coluna certa (item_count vs quantity) | `count_fields` (nível de catálogo) |
| Q011 | Distinguir FK informada de FK existente | `referential_rules` (só no semantic) |
| Q013 | Fazer o JOIN E parar de inflar a saída | `referential_rules` + `response_style` (só no semantic) |
| Q032 | Entender "grão de item" | `money_fields` com `(quantity × unit_price) no grão de item` (nível de catálogo) |
| Q038 | Não acrescentar colunas descritivas | `response_style` (só no semantic) |

**Conclusão legível pro texto do TCC:**

O salto `catalog → semantic` é dominado por dois tipos de regra que não cabem em descrição de coluna:
1. Regras de disambiguação referencial (quando usar JOIN vs IS NOT NULL em presença de FKs órfãs).
2. Regras de estilo (forma da resposta: o que incluir, o que excluir, o que não castar).

Quando a disambiguação cabe em uma descrição de campo (Q005, Q032), o tier catalog já é suficiente — o que justifica os 7.5 pp de ganho catalog sobre technical em gpt-oss-120b. Mas a maior parte do ganho total (18+ pp até semantic) depende das regras estruturais do YAML, não dos comentários de coluna.
