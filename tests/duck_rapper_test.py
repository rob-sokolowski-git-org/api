import pytest

from api.duck_wrapper import DuckRapper


@pytest.fixture
def duckdb() -> DuckRapper:
    return DuckRapper()


@pytest.fixture
def duckdb_with_preload_data() -> DuckRapper:
    core = DuckRapper()
    path: str = "../data/president_polls_historical.csv"
    table_name: str = "president_polls_historical"
    core.import_csv_file(path=path, table_name=table_name)

    return core


def test_import_csv_to_in_memory_table(duckdb) -> None:
    path: str = "../data/president_polls.csv"
    table_name: str = "president_polls"

    duckdb.import_csv_file(path=path, table_name=table_name)

    # read back the table by querying it
    df = duckdb.execute_as_df(query_str="select * from president_polls")
    assert len(df) > 100


def test_execute_as_df(duckdb_with_preload_data) -> None:
    query = f"""
        select
            pp.*
        from president_polls_historical pp
    """
    df = duckdb_with_preload_data.execute_as_df(query_str=query)
    assert len(df) > 100


def test_execute_as_df_with_meta_data(duckdb_with_preload_data) -> None:
    query = "select p.population, sample_size, sponsor_candidate, stage from president_polls_historical p"
    df, df_meta = duckdb_with_preload_data.execute_as_df_with_meta_data(query_str=query)

    assert len(df) > 100
    assert "population" in df.columns
    assert "population" in df_meta["column_name"].tolist()
