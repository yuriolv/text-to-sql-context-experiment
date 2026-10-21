from __future__ import annotations
import argparse, os, sys
from pathlib import Path
import psycopg
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tccsql.config import ROOT, settings
from tccsql.datasets import dataset_dir
from load_dataset import load_commercial
def main():
    p=argparse.ArgumentParser(); p.add_argument("--dataset",default="commercial"); a=p.parse_args(); s=settings(); d=dataset_dir(a.dataset)
    with psycopg.connect(s.database_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO CURRENT_USER")
            cur.execute((d/"schema.sql").read_text(encoding="utf-8"))
        if a.dataset == "commercial": load_commercial(conn)
        else: raise ValueError("Use scripts/prepare_dataset.py para o dataset sintético")
        with conn.cursor() as cur:
            cur.execute("DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='tcc_reader') THEN CREATE ROLE tcc_reader LOGIN PASSWORD 'change_me'; END IF; END $$;")
            cur.execute("GRANT USAGE ON SCHEMA public TO tcc_reader; GRANT SELECT ON ALL TABLES IN SCHEMA public TO tcc_reader; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO tcc_reader")
    print(f"Database ready: {a.dataset}")
if __name__ == "__main__": main()
