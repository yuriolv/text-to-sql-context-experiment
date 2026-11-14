"""Para cada pergunta onde alguma condicao errou, mostra: pergunta, gold, SQL de cada condicao,
resultado do gold e resultado do SQL do modelo (truncado), e um palpite de classificacao."""
import json, sys, os
from pathlib import Path
import psycopg
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from tccsql.database.safety import validate_readonly_sql

URL = os.environ["READONLY_DATABASE_URL"]
RAW = sorted((ROOT/"artifacts/raw").glob("*_final_*.jsonl"))[-1]
rows = [json.loads(l) for l in open(RAW, encoding="utf-8") if l.strip()]
best = {}
for r in rows:
    k = (r["question_id"], r["condition"])
    if k not in best or r["attempt"] > best[k]["attempt"]:
        best[k] = r

questions = {}
for q in open(ROOT/"data/datasets/commercial/questions_final.jsonl", encoding="utf-8"):
    item = json.loads(q); questions[item["id"]] = item

def execute(sql, limit=5):
    try:
        safe = validate_readonly_sql(sql)
    except Exception as e:
        return f"[validation error: {e}]"
    try:
        with psycopg.connect(URL) as c, c.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(f"SET LOCAL statement_timeout = 5000")
            cur.execute(safe)
            rs = cur.fetchmany(limit)
            cols = [d.name for d in cur.description or []]
            return {"cols": cols, "rows": rs, "n_returned": len(rs)}
    except Exception as e:
        return f"[exec error: {e}]"

qids = sorted({qid for (qid, _), r in best.items() if not r.get("correct")})
print(f"Perguntas com pelo menos uma falha: {len(qids)}\n")
for qid in qids:
    q = questions[qid]
    print(f"=== {qid} [{q['category']}] ===")
    print(f"Pergunta: {q['question']}")
    print(f"Gold: {q['gold_sql']}")
    gold_res = execute(q['gold_sql'])
    print(f"Gold result: {gold_res}")
    for cond in ("technical", "semantic"):
        r = best[(qid, cond)]
        status = "OK" if r.get("correct") else (r.get("error_type") or "wrong_result")
        print(f"\n  [{cond}] {status}")
        print(f"  SQL: {r.get('sql')}")
        if not r.get("correct") and r.get("sql"):
            got = execute(r['sql'])
            print(f"  Result: {got}")
    print()
