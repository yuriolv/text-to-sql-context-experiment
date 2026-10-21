from pathlib import Path
import yaml
from pydantic import BaseModel
from tccsql.config import ROOT
class DatasetManifest(BaseModel):
    dataset_id: str; source_type: str; version: str; loader: str
    technical_context: str; semantic_context: str; questions_pilot: str; questions_final: str
def load_manifest(dataset_id: str) -> DatasetManifest:
    path = ROOT / "data" / "datasets" / dataset_id / "manifest.yaml"
    return DatasetManifest.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
def dataset_dir(dataset_id: str) -> Path: return ROOT / "data" / "datasets" / dataset_id
