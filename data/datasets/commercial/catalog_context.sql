-- PostgreSQL public schema. Return one SELECT/WITH query only.
-- Esquema anotado com descricoes em nivel de tabela e de coluna,
-- no formato de catalogo (analogo a COMMENT ON TABLE/COLUMN).

-- collections: catalogo de colecoes do produto com vigencia.
--   collection_id PK
--   name
--   start_date — inicio da vigencia
--   end_date — fim da vigencia

-- families: familias de produto, agrupadas por colecao.
--   family_id PK
--   name
--   collection_id FK -> collections

-- groups: grupos de classificacao de produto.
--   group_id PK
--   name

-- lines: linhas de produto.
--   line_id PK
--   name

-- subgroups: subgrupos de classificacao, aninhados em grupos.
--   subgroup_id PK
--   name
--   group_id FK -> groups

-- representatives: representantes de vendas.
--   representative_id PK
--   name
--   trade_name
--   commission_rate
--   price_table_id
--   active
--   city_id
--   classification

-- customers: clientes.
--   customer_id PK
--   name
--   registered_at — data de cadastro do cliente
--   legal_name
--   city_id
--   representative_id FK -> representatives
--   store_id
--   customer_type_id
--   inactive
--   deidentified_tax_id

-- products: produtos cadastrados no catalogo.
--   product_id PK
--   name
--   category_id
--   list_price — preco de lista cadastrado no produto, nao o praticado em pedido
--   group_id FK -> groups
--   subgroup_id FK -> subgroups
--   collection_id FK -> collections
--   line_id FK -> lines
--   unit_class
--   inactive
--   gender
--   store_id
--   purchase_value — custo de compra registrado
--   cost_value — custo contabil registrado
--   employee_value

-- targets: metas e realizado por representante e periodo.
--   representative_id FK -> representatives
--   month_number
--   year_number
--   achieved_amount — valor realizado pelo representante no periodo da meta; nao e meta planejada
--   month_label
--   target_date — periodo da meta/realizado
--   PK (representative_id, target_date)

-- orders: cabecalho de pedido (1 linha por pedido).
--   order_id PK
--   total_amount — valor final do pedido no grao de cabecalho, ja apos descontos
--   item_count — quantidade de itens informada no cabecalho do pedido
--   customer_id FK -> customers
--   representative_id FK -> representatives
--   payment_id
--   gross_amount — valor bruto do pedido, antes de aplicar descontos
--   discount_amount — desconto concedido no cabecalho do pedido
--   delivered_amount — valor efetivamente entregue do pedido
--   expected_delivery_date — data de entrega prevista
--   status
--   issued_at — data de emissao do pedido
--   representative_classification

-- order_items: item de pedido (N linhas por pedido).
--   order_item_id PK
--   order_id FK -> orders
--   product_id FK -> products
--   quantity — quantidade do item no pedido
--   unit_price — preco unitario praticado no item
--   total_amount — valor do item (quantity x unit_price) no grao de item
--   source_order_id
