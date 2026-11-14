from datetime import date, datetime, timezone
from decimal import Decimal
from tccsql.experiment.evaluator import compare
def test_unordered_decimal_equivalence(): assert compare([(Decimal('1.0'),),(Decimal('2'),)],[(2.0,),(1.0,)])[0]
def test_order_sensitive(): assert not compare([(1,),(2,)],[(2,),(1,)],order_sensitive=True)[0]
def test_int_decimal_equivalence(): assert compare([(Decimal('2016'),1176)],[(2016,1176)])[0]
def test_midnight_datetime_equals_date(): assert compare([(datetime(2016,1,1,tzinfo=timezone.utc),75)],[(date(2016,1,1),75)])[0]
def test_value_change_still_detected(): assert not compare([(Decimal('2016'),1176)],[(2017,1176)])[0]
