import pytest
from tccsql.database.safety import UnsafeSQL, validate_readonly_sql
def test_accepts_select(): assert validate_readonly_sql("SELECT * FROM orders")
@pytest.mark.parametrize("sql",["DELETE FROM orders","SELECT 1; SELECT 2","UPDATE orders SET status='x'","CREATE TABLE x(a int)"])
def test_rejects_writes(sql):
 with pytest.raises(UnsafeSQL):validate_readonly_sql(sql)
