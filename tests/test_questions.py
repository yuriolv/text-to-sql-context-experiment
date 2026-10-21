import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from question_bank import FINAL,PILOT
def test_question_partitions():
 assert len(PILOT)==10 and len(FINAL)==40
 assert {x['id'] for x in PILOT}.isdisjoint({x['id'] for x in FINAL})
 assert {x['category'] for x in FINAL}=={'filters_aggregations','relationships','temporal','business_rules'}
 assert all(x['gold_sql'].upper().startswith('SELECT') for x in FINAL+PILOT)
