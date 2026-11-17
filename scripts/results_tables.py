"""Tabelas derivadas para a seção de Resultados do TCC.

Gera, a partir dos registros brutos em artifacts/raw/:
- per_question_<sufixo>.csv: correção final de cada pergunta em cada condição, com a classe de erro;
- error_classes_<sufixo>.csv: acertos por classe de erro e condição;
- history_iterations.csv: acurácia e McNemar exato de cada iteração do desenho com duas condições.

A classificação das perguntas em classes (A-G) vem de docs/error_taxonomy.md, feita sobre a
rodada 22e3f8ce (gpt-oss-120b). Q017, Q031 e Q036 erram apenas no qwen3.8-27b e não constam
daquele documento; a classe atribuída a elas aqui é uma extensão a revisar.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "artifacts/raw", ROOT / "artifacts/processed"
ORDER = ["technical", "catalog", "semantic"]

CLASSES = {
    "A": ("Escolha de coluna ou grão", ["Q005", "Q032", "Q031", "Q017"]),
    "B": ("FK órfã (JOIN x IS NOT NULL)", ["Q011", "Q013", "Q014", "Q015"]),
    "C": ("Colunas descritivas extras", ["Q013", "Q018", "Q020", "Q037", "Q038"]),
    "D": ("Tipo e formato temporal", ["Q022", "Q027", "Q036"]),
    "E": ("Percentual como fração", ["Q035"]),
    "F": ("Ambiguidade do enunciado", ["Q019", "Q040"]),
    "G": ("Interpretação de média", ["Q039"]),
}
EXTENDED = {"Q017", "Q031", "Q036"}

TIER_RUNS = {"gpt-oss-120b-tiers": "22e3f8ce", "qwen3-27b-tiers": "07a25f55"}
HISTORY = [
    ("inicial", "30bfd1ed"),
    ("pós-D-005", "7f82b1f5"),
    ("pós-D-006", "243a0e26"),
    ("réplica (D-007)", "06a0ccb0"),
]


def final_attempts(run: str) -> pd.DataFrame:
    files = list(RAW.glob(f"*_{run}.jsonl"))
    if len(files) != 1:
        raise SystemExit(f"esperado 1 arquivo bruto para a rodada {run}, encontrado {len(files)}")
    rows = [json.loads(x) for x in files[0].read_text(encoding="utf-8").splitlines() if x.strip()]
    data = pd.DataFrame(rows)
    keep = data.attempt == data.groupby(["question_id", "condition", "repetition"])["attempt"].transform("max")
    return data[keep]


def classes_of(qid: str) -> str:
    return "".join(k for k, (_, ids) in CLASSES.items() if qid in ids)


def mcnemar(a_only: int, b_only: int) -> float:
    n = a_only + b_only
    return binomtest(min(a_only, b_only), n, 0.5, alternative="two-sided").pvalue if n else 1.0


def main() -> None:
    for suffix, run in TIER_RUNS.items():
        final = final_attempts(run)
        wide = final.pivot_table(index=["question_id", "category"], columns="condition",
                                 values="correct", aggfunc="first").reset_index()
        wide[ORDER] = wide[ORDER].astype(int)
        wide["model"] = final.model.iloc[0]
        wide["run"] = run
        wide["error_class"] = wide.question_id.map(classes_of)
        wide["class_extended"] = wide.question_id.isin(EXTENDED)
        wide[["run", "model", "question_id", "category", *ORDER, "error_class", "class_extended"]] \
            .to_csv(OUT / f"per_question_{suffix}.csv", index=False)

        rows = []
        for key, (name, ids) in CLASSES.items():
            sub = wide[wide.question_id.isin(ids)]
            failing = sub[(sub[ORDER] == 0).any(axis=1)]
            # acertos contados só entre as perguntas da classe que erram em ao menos uma condição neste modelo
            rows.append({"class": key, "name": name, "questions_listed": len(ids),
                         "questions_with_error": len(failing),
                         **{c: int(failing[c].sum()) for c in ORDER}})
        pd.DataFrame(rows).to_csv(OUT / f"error_classes_{suffix}.csv", index=False)

    hist = []
    for label, run in HISTORY:
        final = final_attempts(run)
        wide = final.pivot_table(index="question_id", columns="condition", values="correct", aggfunc="first")
        t_only = int((wide.technical & ~wide.semantic).sum())
        s_only = int((~wide.technical & wide.semantic).sum())
        hist.append({"iteration": label, "run": run, "model": final.model.iloc[0], "n": len(wide),
                     "technical_correct": int(wide.technical.sum()), "semantic_correct": int(wide.semantic.sum()),
                     "technical_only": t_only, "semantic_only": s_only, "p_mcnemar": mcnemar(t_only, s_only)})
    pd.DataFrame(hist).to_csv(OUT / "history_iterations.csv", index=False)
    print("ok:", ", ".join(sorted(p.name for p in OUT.glob("*.csv") if p.stem.startswith(("per_question", "error_classes", "history")))))


if __name__ == "__main__":
    main()
