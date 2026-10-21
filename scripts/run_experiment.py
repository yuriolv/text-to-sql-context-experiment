import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src")); from tccsql.config import settings; from tccsql.llm import provider_from_settings; from tccsql.experiment.runner import run
p=argparse.ArgumentParser();p.add_argument("--dataset",default="commercial");p.add_argument("--repetitions",type=int,default=1);a=p.parse_args();run(a.dataset,"final",provider_from_settings(settings()),settings(),a.repetitions)
