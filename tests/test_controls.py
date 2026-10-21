from pathlib import Path
from tccsql.experiment.controls import validate_protocol
def test_frozen_commercial_protocol():
 d=Path("data/datasets/commercial"); qs=[]
 import json
 for name in ("questions_pilot.jsonl","questions_final.jsonl"): qs += [json.loads(x) for x in (d/name).read_text(encoding="utf-8").splitlines()]
 technical=(d/"technical_context.sql").read_text();semantic=(d/"semantic_context.yaml").read_text()
 validate_protocol(d,qs,technical,semantic)
