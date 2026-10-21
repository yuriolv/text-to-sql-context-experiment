from __future__ import annotations
from dataclasses import dataclass
from time import perf_counter
from typing import Any
import psycopg
from psycopg.rows import tuple_row
from .safety import validate_readonly_sql
@dataclass
class QueryResult:
    columns: list[str]; rows: list[tuple[Any, ...]]; latency_ms: float
def execute_readonly(url: str, sql: str, timeout_ms: int = 5000) -> QueryResult:
    sql = validate_readonly_sql(sql); started = perf_counter()
    with psycopg.connect(url, row_factory=tuple_row, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("SET LOCAL statement_timeout = %s", (timeout_ms,))
            cur.execute(sql)
            rows = cur.fetchall(); columns = [x.name for x in cur.description or []]
        conn.rollback()
    return QueryResult(columns, rows, (perf_counter()-started)*1000)
