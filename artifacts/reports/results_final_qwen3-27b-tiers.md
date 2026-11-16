# Resultados do experimento

## Acurácia por condição

| condition   |   n |   accuracy |   ci95_low |   ci95_high |   median_model_latency_ms |   iqr_model_latency_ms |
|:------------|----:|-----------:|-----------:|------------:|--------------------------:|-----------------------:|
| technical   |  40 |      0.575 |   0.421802 |    0.728198 |                   2920.57 |                978.984 |
| catalog     |  40 |      0.6   |   0.448179 |    0.751821 |                   7668.57 |               1001.31  |
| semantic    |  40 |      0.875 |   0.772509 |    0.977491 |                  14789.8  |                186.651 |

## Pares (McNemar exato)

| a         | b        |   a_only_correct |   b_only_correct |   discordant |           p |     p_holm |
|:----------|:---------|-----------------:|-----------------:|-------------:|------------:|-----------:|
| technical | catalog  |                1 |                2 |            3 | 1           | 1          |
| technical | semantic |                0 |               12 |           12 | 0.000488281 | 0.00146484 |
| catalog   | semantic |                0 |               11 |           11 | 0.000976562 | 0.00195312 |

## Latência do modelo (Wilcoxon pareado)

| a         | b        |   median_a_ms |   median_b_ms |           p |      p_holm |
|:----------|:---------|--------------:|--------------:|------------:|------------:|
| technical | catalog  |       2920.57 |       7668.57 | 2.29375e-09 | 2.29375e-09 |
| technical | semantic |       2920.57 |      14789.8  | 5.45697e-12 | 1.09139e-11 |
| catalog   | semantic |       7668.57 |      14789.8  | 1.81899e-12 | 5.45697e-12 |


Os CSVs derivados encontram-se em `artifacts/processed/`. Intervalos da acurácia usam aproximação normal; para amostras pequenas, interpretar junto dos testes pareados.
