

from api.types import DefaultColumn, IntegerColumn, VarcharColumn


def test_column_encoding_varchar_numbers():
    c = VarcharColumn(
        name="test_col",
        type="VARCHAR",
        values=["1", "2", "3"],
    )

    j = c.json()

    # NB: all values must be strings
    assert '"values": ["1", "2", "3"]' in j

def test_column_encoding_varchar_words():
    c = VarcharColumn(
        name="test_col",
        type="VARCHAR",
        values=["apple", "bananas", "3"],
    )

    j = c.json()

    # NB: we want the string "3", not the number 3
    assert '"values": ["apple", "bananas", "3"]' in j


def test_column_encoding_integer():
    c = IntegerColumn(
        name="test_col",
        type="INTEGER",
        values=[1,2,3],
    )

    j = c.json()

    # NB: all values must be integers
    assert '"values": [1, 2, 3]' in j
