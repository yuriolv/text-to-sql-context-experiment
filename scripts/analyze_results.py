from __future__ import annotations
import json, math
from itertools import combinations
from pathlib import Path
import pandas as pd
from scipy.stats import binomtest, wilcoxon
ROOT=Path(__file__).resolve().parents[1]
TIER_ORDER=["technical","catalog","semantic"]
def ci(p,n):
 if not n:return (float("nan"),float("nan"))
 e=1.96*math.sqrt(p*(1-p)/n);return max(0,p-e),min(1,p+e)
def holm(rows):
 """Ajuste de Holm-Bonferroni sobre os p-valores da família de comparações pareadas."""
 m=len(rows); order=sorted(range(m),key=lambda i:rows[i]["p"]); running=0.0
 for rank,i in enumerate(order):
  running=max(running,min(1.0,(m-rank)*rows[i]["p"])); rows[i]["p_holm"]=running
 return rows
def pairwise_mcnemar(pivot, a, b):
 if a not in pivot.columns or b not in pivot.columns: return None
 ba=int(((pivot[a]==True)&(pivot[b]==False)).sum()); bb=int(((pivot[a]==False)&(pivot[b]==True)).sum())
 p=binomtest(min(ba,bb),ba+bb,.5,alternative='two-sided').pvalue if ba+bb else 1.0
 return {"a":a,"b":b,"a_only_correct":ba,"b_only_correct":bb,"discordant":ba+bb,"p":p}
def pairwise_wilcoxon(latency, a, b):
 if a not in latency.columns or b not in latency.columns: return None
 diff=latency[a]-latency[b]
 if not len(diff) or diff.abs().sum()==0: return None
 return {"a":a,"b":b,"median_a_ms":float(latency[a].median()),"median_b_ms":float(latency[b].median()),"p":float(wilcoxon(latency[a],latency[b],zero_method='wilcox').pvalue)}
def main():
 import argparse; parser=argparse.ArgumentParser(); parser.add_argument("--split",default="final",choices=["final","pilot"]); parser.add_argument("--latest-only",action="store_true",default=True); parser.add_argument("--all-runs",dest="latest_only",action="store_false"); parser.add_argument("--run",default=None); parser.add_argument("--suffix",default=None); args=parser.parse_args()
 files=sorted((ROOT/"artifacts/raw").glob(f"*_{args.split}_*.jsonl"))
 if args.run: files = [f for f in files if args.run in f.name]
 elif args.latest_only and files: files = [files[-1]]
 rows=[json.loads(line) for f in files for line in f.read_text(encoding="utf-8").splitlines() if line.strip()]
 if not rows: raise SystemExit(f"Nenhuma execução bruta encontrada para split={args.split}")
 data=pd.DataFrame(rows); final=data[data.attempt==data.groupby(["run_id","question_id","condition","repetition"])["attempt"].transform("max")].copy()
 present=[c for c in TIER_ORDER if c in set(final.condition)]
 summary=[]
 for condition in present:
  g=final[final.condition==condition]; p=float(g.correct.mean()); lo,hi=ci(p,len(g))
  summary.append({"condition":condition,"n":len(g),"accuracy":p,"ci95_low":lo,"ci95_high":hi,"median_model_latency_ms":float(g.model_latency_ms.median()),"iqr_model_latency_ms":float(g.model_latency_ms.quantile(.75)-g.model_latency_ms.quantile(.25))})
 pivot=final.pivot_table(index=["run_id","question_id","repetition"],columns="condition",values="correct",aggfunc="first").dropna()
 latency=final.pivot_table(index=["run_id","question_id","repetition"],columns="condition",values="model_latency_ms",aggfunc="last").dropna()
 pairs=[(a,b) for a,b in combinations(present,2)]
 mcnemar_rows=holm([r for r in (pairwise_mcnemar(pivot,a,b) for a,b in pairs) if r])
 wilcoxon_rows=holm([r for r in (pairwise_wilcoxon(latency,a,b) for a,b in pairs) if r])
 suffix_slug = f"_{args.suffix}" if args.suffix else ""
 summary_df=pd.DataFrame(summary); summary_df.to_csv(ROOT/"artifacts/processed"/f"accuracy{suffix_slug}.csv",index=False)
 final.groupby(["condition","category"]).correct.agg(["count","mean"]).reset_index().to_csv(ROOT/"artifacts/processed"/f"by_category{suffix_slug}.csv",index=False)
 final.error_type.fillna("none").groupby([final.condition,final.error_type.fillna("none")]).size().reset_index(name="count").to_csv(ROOT/"artifacts/processed"/f"error_types{suffix_slug}.csv",index=False)
 mcnemar_df=pd.DataFrame(mcnemar_rows); mcnemar_df.to_csv(ROOT/"artifacts/processed"/f"mcnemar_pairs{suffix_slug}.csv",index=False)
 report=["# Resultados do experimento","","## Acurácia por condição","",summary_df.to_markdown(index=False),""]
 if len(mcnemar_rows):
  report+=["## Pares (McNemar exato)","",mcnemar_df.to_markdown(index=False),""]
 if len(wilcoxon_rows):
  wdf=pd.DataFrame(wilcoxon_rows); report+=["## Latência do modelo (Wilcoxon pareado)","",wdf.to_markdown(index=False),""]
 report+=["","Os CSVs derivados encontram-se em `artifacts/processed/`. Intervalos da acurácia usam aproximação normal; para amostras pequenas, interpretar junto dos testes pareados."]
 out=(ROOT/"artifacts/reports"/f"results_{args.split}{suffix_slug}.md"); out.write_text("\n".join(report)+"\n",encoding="utf-8"); print(out)
if __name__=="__main__":main()
