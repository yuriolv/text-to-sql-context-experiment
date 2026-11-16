# Resultados do experimento

## Acurácia por condição

| condition   |   n |   accuracy |   ci95_low |   ci95_high |   median_model_latency_ms |   iqr_model_latency_ms |
|:------------|----:|-----------:|-----------:|------------:|--------------------------:|-----------------------:|
| technical   |  40 |      0.625 |   0.474969 |    0.775031 |                   1399.89 |                1280.16 |
| catalog     |  40 |      0.7   |   0.557985 |    0.842015 |                   1394.41 |                4073.34 |
| semantic    |  40 |      0.825 |   0.707247 |    0.942753 |                   7898.2  |                8339.4  |

## Pares (McNemar exato)

| a         | b        |   a_only_correct |   b_only_correct |   discordant |         p |    p_holm |
|:----------|:---------|-----------------:|-----------------:|-------------:|----------:|----------:|
| technical | catalog  |                0 |                3 |            3 | 0.25      | 0.359375  |
| technical | semantic |                1 |                9 |           10 | 0.0214844 | 0.0644531 |
| catalog   | semantic |                2 |                7 |            9 | 0.179688  | 0.359375  |

## Latência do modelo (Wilcoxon pareado)

| a         | b        |   median_a_ms |   median_b_ms |           p |      p_holm |
|:----------|:---------|--------------:|--------------:|------------:|------------:|
| technical | catalog  |       1399.89 |       1394.41 | 0.0481645   | 0.0481645   |
| technical | semantic |       1399.89 |       7898.2  | 7.82165e-11 | 2.3465e-10  |
| catalog   | semantic |       1394.41 |       7898.2  | 1.38607e-09 | 2.77214e-09 |


Os CSVs derivados encontram-se em `artifacts/processed/`. Intervalos da acurácia usam aproximação normal; para amostras pequenas, interpretar junto dos testes pareados.
