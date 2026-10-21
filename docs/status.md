# Estado atual do projeto

Atualizado em 21/10/2026.

## Objetivo

O projeto implementa um experimento controlado de Text-to-SQL para comparar duas condições: contexto exclusivamente técnico e contexto enriquecido com informações semânticas. Agente, modelo, perguntas, snapshot da base e demais parâmetros permanecem constantes entre as condições.

## Concluído

- Estrutura Python e comandos de preparação, carga, piloto, experimento e análise implementados.
- Avaliação local das bases candidatas concluída, sem envio de valores de linhas a serviços externos.
- Base `commercial` selecionada para o estudo, com uso autorizado e transformação de 11 planilhas para um esquema relacional PostgreSQL.
- Base `financeiro` excluída por falta de confirmação específica de autorização e privacidade.
- Dataset `synthetic_commercial` mantido para testes automatizados.
- Esquema, contexto técnico, contexto semântico, regras de negócio e bancos de perguntas do piloto e da coleta final preparados.
- Controles de pareamento e contrabalanceamento implementados.
- Nove testes automatizados aprovados em 21/10/2026.

## Ponto de parada

A preparação do código e do protocolo está concluída. A base ainda não foi carregada no PostgreSQL e não existem registros de execução em `artifacts/raw/` nem relatórios experimentais em `artifacts/reports/`. O arquivo local `.env` também ainda não foi criado.

## Próximos passos

1. Copiar `.env.example` para `.env` e preencher as configurações locais.
2. Iniciar o PostgreSQL com `docker compose up -d`.
3. Executar `make setup` para preparar e carregar a base `commercial`.
4. Executar `make test` e confirmar novamente a suíte automatizada.
5. Executar `make pilot`.
6. Revisar o piloto, registrar o número definitivo de repetições e eventuais ajustes metodológicos.
7. Executar `make experiment` e `make analyze`.

## Observações para versionamento

- `.env`, planilhas de origem, caches e resultados brutos gerados localmente não devem ser enviados ao GitHub.
- Os artefatos de avaliação agregados permanecem versionáveis porque não contêm valores de linhas.
- As decisões metodológicas e de privacidade estão registradas em `docs/decisions.md`.
