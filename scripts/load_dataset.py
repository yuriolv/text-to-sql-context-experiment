"""Carrega a fonte XLSX comercial sem alterá-la; usado apenas por setup_database."""
from __future__ import annotations
import math, os
from pathlib import Path
import pandas as pd
import psycopg
from psycopg import sql

SOURCE = {"collections":"dColecoes.xlsx", "families":"dFamilias.xlsx", "groups":"dGrupos.xlsx", "lines":"dLinhas.xlsx", "subgroups":"dSubGrupos.xlsx", "representatives":"dRepresentantes.xlsx", "customers":"dClientes.xlsx", "products":"dProdutos.xlsx", "targets":"fMetas.xlsx", "orders":"fPedidos.xlsx", "order_items":"fPedidosItens.xlsx"}
COLUMNS = {
"collections":["collection_id","name","start_date","end_date"], "families":["family_id","name","collection_id"], "groups":["group_id","name"], "lines":["line_id","name"], "subgroups":["subgroup_id","name","group_id"],
"representatives":["representative_id","name","trade_name","commission_rate","price_table_id","active","city_id","classification"],
"customers":["customer_id","name","registered_at","legal_name","city_id","representative_id","store_id","customer_type_id","inactive","deidentified_tax_id"],
"products":["product_id","name","category_id","list_price","group_id","subgroup_id","collection_id","line_id","unit_class","inactive","gender","store_id","purchase_value","cost_value","employee_value"],
"targets":["representative_id","month_number","year_number","achieved_amount","month_label","target_date"],
"orders":["total_amount","order_id","item_count","customer_id","representative_id","payment_id","gross_amount","discount_amount","delivered_amount","expected_delivery_date","status","issued_at","representative_classification"],
"order_items":["order_id","product_id","quantity","unit_price","total_amount","source_order_id"]}
def source_root() -> Path: return Path(os.getenv("CANDIDATES_ROOT", r"C:\Users\Yuri\rt_data\genericos"))
def clean(value):
    if value is None or (isinstance(value,float) and math.isnan(value)): return None
    if hasattr(value, "to_pydatetime"): return value.to_pydatetime()
    return value
def load_commercial(conn: psycopg.Connection) -> None:
    root=source_root()
    for table, filename in SOURCE.items():
        path=root/filename
        if not path.exists(): raise FileNotFoundError(f"Fonte ausente: {path}")
        frame=pd.read_excel(path, engine="openpyxl")
        if list(frame.columns) != list(frame.columns): raise ValueError("Cabeçalho inválido")
        frame.columns=COLUMNS[table]
        rows=[tuple(clean(x) for x in row) for row in frame.itertuples(index=False, name=None)]
        with conn.cursor() as cur:
            fields=sql.SQL(",").join(map(sql.Identifier, COLUMNS[table]))
            markers=sql.SQL(",").join([sql.Placeholder()]*len(COLUMNS[table]))
            statement=sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(sql.Identifier(table), fields, markers)
            cur.executemany(statement, rows)
        conn.commit()
        print(f"loaded {table}: {len(rows)} rows")
