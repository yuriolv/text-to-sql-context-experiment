from __future__ import annotations
import json, math
from pathlib import Path
import pandas as pd
from scipy.stats import binomtest, wilcoxon
ROOT=Path(__file__).resolve().parents[1]
def ci(p,n):
 if not n:return (float("nan"),float("nan"))
 e=1.96*math.sqrt(p*(1-p)/n);return max(0,p-e),min(1,p+e)
def main():
 files=sorted((ROOT/"artifacts/raw").glob("*.jsonl")); rows=[json.loads(line) for f in files for line in f.read_text(encoding="utf-8").splitlines()]
 if not rows: raise SystemExit("Nenhuma execução bruta encontrada")
 data=pd.DataFrame(rows); final=data[data.attempt==data.groupby(["run_id","question_id","condition","repetition"])["attempt"].transform("max")].copy()
 summary=[]
 for condition,g in final.groupby("condition"):
  p=float(g.correct.mean()); lo,hi=ci(p,len(g));summary.append({"condition":condition,"n":len(g),"accuracy":p,"ci95_low":lo,"ci95_high":hi,"median_model_latency_ms":g.model_latency_ms.median(),"iqr_model_latency_ms":g.model_latency_ms.quantile(.75)-g.model_latency_ms.quantile(.25)})
 pivot=final.pivot_table(index=["run_id","question_id","repetition"],columns="condition",values="correct",aggfunc="first").dropna()
 b=int(((pivot.technical==True)&(pivot.semantic==False)).sum());c=int(((pivot.technical==False)&(pivot.semantic==True)).sum());mcnemar=binomtest(min(b,c)*2,b+c,.5).pvalue if b+c else 1.0
 latency=final.pivot_table(index=["run_id","question_id","repetition"],columns="condition",values="model_latency_ms",aggfunc="last").dropna()
 wilcoxon_p="not available"
 if len(latency) and (latency.semantic-latency.technical).abs().sum()>0:
  wilcoxon_p=f"{wilcoxon(latency.semantic,latency.technical,zero_method='wilcox').pvalue:.6g}"
 summary_df=pd.DataFrame(summary);summary_df.to_csv(ROOT/"artifacts/processed/accuracy.csv",index=False)
 final.groupby(["condition","category"]).correct.agg(["count","mean"]).reset_index().to_csv(ROOT/"artifacts/processed/by_category.csv",index=False)
 final.error_type.fillna("none").groupby([final.condition,final.error_type.fillna("none")]).size().reset_index(name="count").to_csv(ROOT/"artifacts/processed/error_types.csv",index=False)
 report=["# Resultados do experimento","",summary_df.to_markdown(index=False),"",f"Diferença absoluta (semântica − técnica): {summary_df.set_index('condition').accuracy.get('semantic',float('nan'))-summary_df.set_index('condition').accuracy.get('technical',float('nan')):.4f}.",f"","## Pares","",f"Técnica correta / semântica incorreta: {b}; técnica incorreta / semântica correta: {c}; teste exato de McNemar: p={mcnemar:.6g}.",f"Wilcoxon pareado para latência do modelo: p={wilcoxon_p}.","","Os CSVs derivados encontram-se em `artifacts/processed/`. Intervalos da acurácia usam aproximação normal; para amostras pequenas, interpretar junto do teste pareado."]
 (ROOT/"artifacts/reports/results.md").write_text("\n".join(report)+"\n",encoding="utf-8");print(ROOT/"artifacts/reports/results.md")
if __name__=="__main__":main()
