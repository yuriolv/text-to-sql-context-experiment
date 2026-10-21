from __future__ import annotations
from collections import Counter
from datetime import date, datetime
from decimal import Decimal
import hashlib, json, math
def atom(value, tolerance):
 if value is None:return ["null",None]
 if isinstance(value,(datetime,date)):return ["date",value.isoformat()]
 if isinstance(value,Decimal): value=float(value)
 if isinstance(value,float): return ["number",round(value/max(tolerance,1e-12))*max(tolerance,1e-12)]
 return [type(value).__name__,value]
def normalized(rows, tolerance, ordered):
 values=[tuple(atom(v,tolerance) for v in row) for row in rows]
 return values if ordered else sorted(values,key=lambda x:json.dumps(x,sort_keys=True,default=str))
def compare(actual,gold,tolerance=1e-6,order_sensitive=False):
 a=normalized(actual,tolerance,order_sensitive); g=normalized(gold,tolerance,order_sensitive)
 payload=json.dumps(a,sort_keys=True,default=str); return a==g, hashlib.sha256(payload.encode()).hexdigest()
