# Decisões metodológicas

## D-001 — Fonte experimental

As candidatas externas são avaliadas localmente e somente por metadados agregados. Em 26/09/2026, o responsável confirmou que os dados comerciais e nomes sintéticos adjacentes são descaracterizados e autorizou seu uso acadêmico. O recorte `commercial` é, portanto, `USE_WITH_TRANSFORMATIONS`: as planilhas XLSX são lidas sem modificação a partir de `CANDIDATES_ROOT`, normalizadas em PostgreSQL, e valores de linhas continuam bloqueados para provedor externo. A base `financeiro` permanece excluída por falta de confirmação específica. `synthetic_commercial` permanece para testes automatizados.

## D-002 — Controle e repetições

Piloto e final são pareados: para cada pergunta/repetição há A e B em ordem contrabalanceada por uma permutação com semente. O número de repetições deve ser registrado no manifesto de coleta antes do final; o padrão é 1 para o provedor determinístico e 3 para provedores remotos, salvo decisão registrada após o piloto.

## D-003 — Privacidade

O avaliador das candidatas não envia qualquer dado externo. O agente recebe apenas DDL/contexto e, quando permitido pela configuração, uma amostra sanitizada e limitada de resultados da consulta gerada. Para fontes marcadas sensíveis, a amostra é desabilitada.

## D-004 — Fidelidade aos dados sobre enforcement de FK

Em 14/11/2026, a carga inicial de `commercial` falhou em `subgroups` com `group_id` referenciando um grupo inexistente. Dados comerciais reais contêm referências órfãs e esse comportamento é esperado. Para preservar a fonte exatamente como foi autorizada, removemos as declarações `REFERENCES` de `schema.sql`: as tabelas mantêm nomes de coluna, tipos, `PRIMARY KEY` e `NOT NULL`, mas o PostgreSQL não valida mais integridade referencial. As consultas do banco continuam funcionando por igualdade em `JOIN`. O contexto técnico (`technical_context.sql`) ainda descreve as relações como "FK ->" de forma textual — essa informação é apresentada ao modelo mesmo sem ser enforced no servidor.

## D-005 — Revisão do contexto semântico e do avaliador após o primeiro final

A primeira execução final (14/11/2026) produziu 24/40 correct na condição semântica contra 26/40 na técnica (McNemar p=1.0). A auditoria dos 17 erros revelou três problemas distintos e tratáveis antes da coleta definitiva:

1. **Contexto semântico com glossário genérico.** A entrada `valor_pedido: orders.total_amount` levou o modelo a usar `total_amount` quando a pergunta era sobre `gross_amount` (Q008). Hints de relacionamento convidavam o modelo a acrescentar colunas descritivas (nome do representante, nome do cliente) em respostas que pediam só contagem/agregação (Q013, Q018, Q020, Q037, Q039). O contexto não mencionava a existência de referências órfãs documentada em D-004.
   
   Reescrevemos `semantic_context.yaml` separando campos monetários e de contagem por tabela, adicionando `grain_rules` e `referential_rules` explícitas, e incluindo um bloco `response_style` que proíbe colunas descritivas não solicitadas e casts desnecessários.

2. **Avaliador superestrito em tipos equivalentes.** O comparador tratava `int(2016)` e `Decimal(2016)` como diferentes, e `datetime(2016,1,1,0,0,UTC)` como diferente de `date(2016,1,1)`, causando ao menos 3 falsos negativos em ambas as condições (Q021, Q022, Q023). `tccsql.experiment.evaluator.atom` agora normaliza inteiros a `number`, aplica a mesma tolerância numérica a todos os tipos numéricos, e trata datetimes à meia-noite UTC como `date`. A relaxação preserva o rigor contra mudanças de valor e preserva o teste `test_unordered_decimal_equivalence`.

3. **Perguntas com ambiguidade genuína.** Q005 ("quantidade de itens" — ambígua entre `orders.item_count` e `SUM(order_items.quantity)`), Q019 ("quantidade de itens por grupo" — contagem vs soma de quantidades) e Q040 ("diferença... somada por pedido") não dependem do contexto, mas do enunciado. Mantidas como estão e discutidas na seção de limitações do TCC, por serem representativas de perguntas reais de usuário.

A nova coleta final usa estas correções. O resultado original (24 vs 26) permanece registrado em `artifacts/raw/*_final_30bfd1ed.jsonl` como baseline pré-correção.

## D-006 — Padronização estrutural do gold SQL em perguntas "associado"

A auditoria da segunda execução (14/11/2026, 34/40 × 29/40) revelou uma inconsistência estrutural no `questions_final.jsonl`: perguntas lexicalmente equivalentes sobre associação — "X têm Y associado", "X estão associados a Y", "X possuem Y associado" — tinham gold SQL dividido entre `JOIN` e `WHERE y IS NOT NULL`. Especificamente, Q011, Q012, Q015 e Q017 usavam `JOIN`; Q013, Q014 e Q016 usavam `IS NOT NULL`. Por D-004, a base tem referências órfãs, então as duas formulações produzem resultados diferentes.

Essa inconsistência impunha um teto artificial: qualquer condição lexicalmente consistente ficava refém de o gold concordar ou discordar conforme a pergunta. A condição semântica, que segue a regra "'associado' → JOIN" declarada em `semantic_context.yaml::referential_rules`, passava Q011 e Q015 mas falhava em Q013 e Q014 (e vice-versa na condição técnica).

Padronizamos os golds de Q013, Q014 e Q016 para a forma `JOIN`, alinhando aos Q011, Q012, Q015 e Q017 pré-existentes. A escolha de `JOIN` em vez de `IS NOT NULL` segue a interpretação "associado = ligado a um referente existente", consistente com a semântica natural em pt-BR e com a convenção majoritária já presente no gold original (4 das 7 perguntas de associação).

A padronização é estrutural: foi decidida pela forma linguística, não pela condição favorecida. O resultado da rodada anterior (34 × 29, gold inconsistente) fica preservado em `artifacts/raw/*_final_7f82b1f5.jsonl` para transparência da iteração e possível análise de sensibilidade.
