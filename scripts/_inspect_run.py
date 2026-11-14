import json, sys
from collections import defaultdict
path = sys.argv[1]
rows = [json.loads(l) for l in open(path, encoding="utf-8")]
print(f"total records: {len(rows)}")
best = {}
for r in rows:
    k = (r["question_id"], r["condition"])
    if k not in best or r["attempt"] > best[k]["attempt"]:
        best[k] = r
by_cond = defaultdict(lambda: {"correct": 0, "exec_fail": 0, "val_fail": 0, "n": 0})
print("\nultima tentativa por pergunta/condicao:")
for (qid, cond), r in sorted(best.items()):
    c = by_cond[cond]; c["n"] += 1
    if r.get("correct"): c["correct"] += 1
    elif r.get("error_type") == "database": c["exec_fail"] += 1
    elif r.get("error_type") == "validation": c["val_fail"] += 1
    status = "OK" if r.get("correct") else (r.get("error_type") or "wrong_result")
    sql = (r.get("sql") or "")[:70].replace("\n", " ")
    print(f"  {qid} {cond:9s} att={r['attempt']} {status:12s} {sql}")
print("\nresumo por condicao:")
for cond, c in sorted(by_cond.items()):
    print(f"  {cond}: correct={c['correct']}/{c['n']}  exec_fail={c['exec_fail']}  val_fail={c['val_fail']}")
