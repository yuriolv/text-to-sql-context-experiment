# Resultados do experimento

| condition   |   n |   accuracy |   ci95_low |   ci95_high |   median_model_latency_ms |   iqr_model_latency_ms |
|:------------|----:|-----------:|-----------:|------------:|--------------------------:|-----------------------:|
| semantic    |  40 |       0.85 |   0.739342 |    0.960658 |                  10313.7  |                873.043 |
| technical   |  40 |       0.55 |   0.395825 |    0.704175 |                   3179.79 |                386.633 |

Diferença absoluta (semântica − técnica): 0.3000.

## Pares

Técnica correta / semântica incorreta: 0; técnica incorreta / semântica correta: 12; teste exato de McNemar: p=0.000488281.
Wilcoxon pareado para latência do modelo: p=1.27329e-11.

Os CSVs derivados encontram-se em `artifacts/processed/`. Intervalos da acurácia usam aproximação normal; para amostras pequenas, interpretar junto do teste pareado.
