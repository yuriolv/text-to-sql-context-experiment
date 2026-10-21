# Avaliação das bases candidatas

Avaliação feita localmente, por estrutura e estatísticas agregadas; nenhum valor de linha foi exposto.

| Base | Classificação | Justificativa |
|---|---|---|
| comercial | USE_WITH_TRANSFORMATIONS | Autorização confirmada; 11 tabelas relacionadas, normalização XLSX→PostgreSQL necessária. |
| financeiro | DO_NOT_USE | Autorização específica e privacidade não confirmadas. |
| CSVs sintéticos fragmentados | DO_NOT_USE | Não formam snapshot relacional íntegro. |

## Comercial

Foram identificadas 11 planilhas: dimensões de clientes, produtos, classificação de produtos e representantes; fatos de pedidos, itens e metas. Há datas, status e medidas monetárias. Relações são inferidas e passam a ser FKs no schema preparado. Risco analítico central: `orders` → `order_items` é 1:N e duplica medidas de cabeçalho quando agregado após o join. As datas de emissão, entrega prevista, cadastro, vigência de coleção e meta têm semânticas distintas.

O campo de identificação descaracterizado e nomes não são enviados a modelos externos; a amostra de resultados para o agente é desabilitada no dataset.

Os perfis completos (somente contagens, cabeçalhos, tipos, nulos e duplicidades) estão em `profiles/`.
