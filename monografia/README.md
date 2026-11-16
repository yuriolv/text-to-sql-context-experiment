# Monografia (LaTeX)

Texto do TCC, em abnTeX2 ajustado ao Guia de Normalização da UECE 2026.

## Compilar

```
latexmk -pdf main.tex
```

Ou no Overleaf, enviando a pasta `monografia/` com o compilador pdfLaTeX.

## Estrutura

- `config/preambulo.tex`: formatação conforme o guia (margens, fonte, títulos, paginação, legendas).
- `config/dados.tex`: identificação do trabalho, orientador e banca.
- `pretextuais/`, `textuais/`, `postextuais/`: uma seção primária por arquivo.
- `referencias.bib`: referências. Toda entrada precisa ser conferida na fonte.

## Convenções

- `\pendente{...}` aparece em vermelho no PDF e marca um dado ainda não confirmado.
- `\begin{esboco} ... \end{esboco}` guarda o roteiro do conteúdo e as fontes de cada seção. Não aparece no PDF.
- Todo número citado no texto precisa vir de `artifacts/` ou `docs/`.
- O resultado principal é o desenho de 3 níveis (`artifacts/reports/results_final_*-tiers.md`).
