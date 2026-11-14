# Resultados do experimento

| condition   |   n |   accuracy |   ci95_low |   ci95_high |   median_model_latency_ms |   iqr_model_latency_ms |
|:------------|----:|-----------:|-----------:|------------:|--------------------------:|-----------------------:|
| semantic    |  40 |      0.85  |   0.739342 |    0.960658 |                   5717.08 |                5550.96 |
| technical   |  40 |      0.725 |   0.586624 |    0.863376 |                   1550.89 |                1284.37 |

Diferença absoluta (semântica − técnica): 0.1250.

## Pares

Técnica correta / semântica incorreta: 2; técnica incorreta / semântica correta: 7; teste exato de McNemar: p=0.179688.
Wilcoxon pareado para latência do modelo: p=9.74978e-10.

Os CSVs derivados encontram-se em `artifacts/processed/`. Intervalos da acurácia usam aproximação normal; para amostras pequenas, interpretar junto do teste pareado.
