# Decisões metodológicas

## D-001 — Fonte experimental

As candidatas externas são avaliadas localmente e somente por metadados agregados. Em 26/09/2026, o responsável confirmou que os dados comerciais e nomes sintéticos adjacentes são descaracterizados e autorizou seu uso acadêmico. O recorte `commercial` é, portanto, `USE_WITH_TRANSFORMATIONS`: as planilhas XLSX são lidas sem modificação a partir de `CANDIDATES_ROOT`, normalizadas em PostgreSQL, e valores de linhas continuam bloqueados para provedor externo. A base `financeiro` permanece excluída por falta de confirmação específica. `synthetic_commercial` permanece para testes automatizados.

## D-002 — Controle e repetições

Piloto e final são pareados: para cada pergunta/repetição há A e B em ordem contrabalanceada por uma permutação com semente. O número de repetições deve ser registrado no manifesto de coleta antes do final; o padrão é 1 para o provedor determinístico e 3 para provedores remotos, salvo decisão registrada após o piloto.

## D-003 — Privacidade

O avaliador das candidatas não envia qualquer dado externo. O agente recebe apenas DDL/contexto e, quando permitido pela configuração, uma amostra sanitizada e limitada de resultados da consulta gerada. Para fontes marcadas sensíveis, a amostra é desabilitada.
