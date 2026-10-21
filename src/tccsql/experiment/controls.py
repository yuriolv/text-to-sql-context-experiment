from __future__ import annotations
import hashlib,json
from pathlib import Path
def digest(path:Path): return hashlib.sha256(path.read_bytes()).hexdigest()
def validate_protocol(dataset_dir:Path, questions:list[dict], technical:str, semantic:str):
    assert technical and semantic and semantic != technical and "SEMÂNTICA" not in technical
    assert all("gold_sql" in q and q["gold_sql"] not in technical and q["gold_sql"] not in semantic for q in questions), "gabarito vazou no contexto"
    assert len({q["id"] for q in questions})==len(questions), "ids duplicados"
    frozen=(dataset_dir/"checksums.sha256").read_text(encoding="utf-8")
    expected={line.split("  ",1)[1]:line.split("  ",1)[0] for line in frozen.splitlines() if "  " in line}
    for relative,checksum in expected.items():
        if relative=="checksums.sha256": continue
        if digest(dataset_dir/relative)!=checksum: raise ValueError(f"arquivo congelado alterado: {relative}")
    return {"technical_hash":hashlib.sha256(technical.encode()).hexdigest(),"semantic_hash":hashlib.sha256(semantic.encode()).hexdigest()}
