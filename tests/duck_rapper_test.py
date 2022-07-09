import pytest

from api.duck_rapper import DuckRapper
from api.types import DuckDbQueryResponse
from env_config import CONFIG, EnvironmentConfig


@pytest.fixture
def duckdb() -> DuckRapper:
    return DuckRapper(env_config=CONFIG)


@pytest.fixture
def duckdb_with_preload_data() -> DuckRapper:
    duckdb = DuckRapper(env_config=CONFIG)
    path: str = "./data/president_polls_historical.csv"
    table_name: str = "president_polls_historical"
    duckdb.import_csv_file(path=path, table_name=table_name)

    return duckdb


def test_import_csv_to_in_memory_table(duckdb) -> None:
    path: str = "./data/president_polls.csv"
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
    query = "select p.population, p.sample_size, p.sponsor_candidate, p.stage from president_polls_historical p"
    df, df_meta = duckdb_with_preload_data.execute_as_df_with_meta_data(query_str=query)

    assert len(df) > 100
    assert "population" in df.columns
    assert "population" in df_meta["column_name"].tolist()


def test_map_to_duckdb_response(duckdb_with_preload_data) -> None:
    # NB: We assume this query works, and test mapping of this result. Testing of the query & meta data is tested
    #     elsewhere
    query = "select p.population, p.sample_size, p.sponsor_candidate, p.stage from president_polls_historical p"
    df_data, df_metadata = duckdb_with_preload_data.execute_as_df_with_meta_data(query_str=query)

    response: DuckDbQueryResponse = duckdb_with_preload_data.map_response(df_data=df_data, df_metadata=df_metadata)

    assert len(response.columns) == 4
    assert response.columns[0].name == "population"
    assert response.columns[1].name == "sample_size"
    assert response.columns[2].name == "sponsor_candidate"
    assert response.columns[3].name == "stage"
