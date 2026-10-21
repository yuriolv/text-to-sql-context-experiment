from decimal import Decimal
from tccsql.experiment.evaluator import compare
def test_unordered_decimal_equivalence(): assert compare([(Decimal('1.0'),),(Decimal('2'),)],[(2.0,),(1.0,)])[0]
def test_order_sensitive(): assert not compare([(1,),(2,)],[(2,),(1,)],order_sensitive=True)[0]
