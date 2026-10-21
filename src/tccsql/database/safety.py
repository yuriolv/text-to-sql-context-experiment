from __future__ import annotations
import sqlglot
from sqlglot import exp
class UnsafeSQL(ValueError): pass
def validate_readonly_sql(sql: str) -> str:
    try: statements = sqlglot.parse(sql, read="postgres")
    except Exception as error: raise UnsafeSQL(f"SQL inválido: {error}") from error
    if len(statements) != 1: raise UnsafeSQL("Múltiplas instruções não são permitidas")
    tree = statements[0]
    if not isinstance(tree, (exp.Select, exp.Union, exp.With, exp.Subquery)) or not tree.find(exp.Select):
        raise UnsafeSQL("Apenas SELECT ou WITH terminado em SELECT é permitido")
    forbidden = (exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop, exp.Alter, exp.Command, exp.Grant, exp.Revoke, exp.Copy)
    if any(tree.find(kind) for kind in forbidden): raise UnsafeSQL("Comando não permitido")
    for table in tree.find_all(exp.Table):
        if table.db and table.db.lower() not in {"public"}: raise UnsafeSQL("Acesso a esquema não permitido")
    return tree.sql(dialect="postgres")
