import pytest

from api.duck_wrapper import DuckCore


@pytest.fixture
def duck_core() -> DuckCore:
    return DuckCore()


@pytest.fixture
def duck_core_preloaded() -> DuckCore:
    core = DuckCore()
    path: str = "../data/president_polls_historical.csv"
    table_name: str = "president_polls_historical"
    core.import_csv_file(path=path, table_name=table_name)

    return core


def test_import_csv_to_in_memory_table(duck_core: DuckCore) -> None:
    path: str = "../data/president_polls.csv"
    table_name: str = "president_polls"

    duck_core.import_csv_file(path=path, table_name=table_name)

    # read back the table by querying it
    df = duck_core.execute_as_df(query_str="select * from president_polls")
    assert len(df) > 100


def test_execute_as_df(duck_core_preloaded: DuckCore) -> None:
    query = f"""
        select
            pp.*
        from president_polls_historical pp
    """
    df = duck_core_preloaded.execute_as_df(query_str=query)
    assert len(df) > 100