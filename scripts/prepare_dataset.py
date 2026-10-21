from __future__ import annotations
import argparse, hashlib, sys, os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src")); from tccsql.datasets import dataset_dir
from question_bank import write_questions
def main():
 p=argparse.ArgumentParser();p.add_argument("--dataset",default="commercial");a=p.parse_args();d=dataset_dir(a.dataset)
 if a.dataset != "commercial": raise NotImplementedError("O gerador sintético será mantido para a suíte de testes; a preparação operacional é comercial.")
 write_questions(d)
 # Congela a identidade dos arquivos-fonte sem copiá-los ou revelar conteúdo.
 source=Path(os.getenv("CANDIDATES_ROOT",r"C:\Users\Yuri\rt_data\genericos"))
 names=["dColecoes.xlsx","dFamilias.xlsx","dGrupos.xlsx","dLinhas.xlsx","dSubGrupos.xlsx","dRepresentantes.xlsx","dClientes.xlsx","dProdutos.xlsx","fMetas.xlsx","fPedidos.xlsx","fPedidosItens.xlsx"]
 source_lines=[]
 for name in names:
  path=source/name
  if path.exists(): source_lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {name}\n")
 (d/"load"/"source_checksums.sha256").write_text("".join(source_lines),encoding="utf-8")
 files=[x for x in d.rglob("*") if x.is_file() and x.name!="checksums.sha256"]
 (d/"checksums.sha256").write_text("".join(f"{hashlib.sha256(x.read_bytes()).hexdigest()}  {x.relative_to(d).as_posix()}\n" for x in sorted(files)),encoding="utf-8")
 print(f"Prepared {a.dataset}; {len(files)} frozen files")
if __name__=="__main__":main()
