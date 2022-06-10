import pytest

from api.duck_wrapper import DuckCore


@pytest.fixture
def duck_core() -> DuckCore:
    return DuckCore()


def test_import_csv_to_in_memory_table(duck_core: DuckCore) -> None:
    path: str = "./data/president_polls.csv"
    table_name: str = "president_polls"

    duck_core.import_csv_file(path=path, table_name=table_name)

    # read back the table by querying it
    df = duck_core.execute_as_df(query_str="select * from president_polls")
    assert len(df) > 100
