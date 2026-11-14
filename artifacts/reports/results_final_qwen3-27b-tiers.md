# Resultados do experimento

## Acurácia por condição

| condition   |   n |   accuracy |   ci95_low |   ci95_high |   median_model_latency_ms |   iqr_model_latency_ms |
|:------------|----:|-----------:|-----------:|------------:|--------------------------:|-----------------------:|
| technical   |  39 |   0.589744 |   0.435366 |    0.744121 |                   2920.51 |                980.94  |
| catalog     |  39 |   0.615385 |   0.462695 |    0.768075 |                   7663.01 |               1011.96  |
| semantic    |  39 |   0.871795 |   0.766869 |    0.976721 |                  14790.2  |                167.718 |

## Pares (McNemar exato)

| a         | b        |   a_only_correct |   b_only_correct |   discordant |           p |
|:----------|:---------|-----------------:|-----------------:|-------------:|------------:|
| technical | catalog  |                1 |                2 |            3 | 1           |
| technical | semantic |                0 |               11 |           11 | 0.000976562 |
| catalog   | semantic |                0 |               10 |           10 | 0.00195312  |

## Latência do modelo (Wilcoxon pareado)

| a         | b        |   median_a_ms |   median_b_ms |           p |
|:----------|:---------|--------------:|--------------:|------------:|
| technical | catalog  |       2920.51 |       7663.01 | 3.889e-09   |
| technical | semantic |       2920.51 |      14790.2  | 1.09139e-11 |
| catalog   | semantic |       7663.01 |      14790.2  | 3.63798e-12 |


Os CSVs derivados encontram-se em `artifacts/processed/`. Intervalos da acurácia usam aproximação normal; para amostras pequenas, interpretar junto dos testes pareados.
