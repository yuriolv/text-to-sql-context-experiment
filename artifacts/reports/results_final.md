# Resultados do experimento

| condition   |   n |   accuracy |   ci95_low |   ci95_high |   median_model_latency_ms |   iqr_model_latency_ms |
|:------------|----:|-----------:|-----------:|------------:|--------------------------:|-----------------------:|
| semantic    |  40 |      0.875 |   0.772509 |    0.977491 |                   3438.27 |                3533.13 |
| technical   |  40 |      0.65  |   0.502186 |    0.797814 |                   1488.1  |                1005.06 |

Diferença absoluta (semântica − técnica): 0.2250.

## Pares

Técnica correta / semântica incorreta: 0; técnica incorreta / semântica correta: 9; teste exato de McNemar: p=0.00390625.
Wilcoxon pareado para latência do modelo: p=9.44651e-05.

Os CSVs derivados encontram-se em `artifacts/processed/`. Intervalos da acurácia usam aproximação normal; para amostras pequenas, interpretar junto do teste pareado.
