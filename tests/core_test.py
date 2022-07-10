import os
import random

import pytest

from api.core import CoreBusinessLogic, TableRef
from api.types import DuckDbQueryResponse, TableRefGroup
from env_config import CONFIG, EnvironmentConfig
import time
from os.path import exists

TEST_TEMP_DIR = "./tests/temp"

@pytest.fixture
def core() -> CoreBusinessLogic:
    return CoreBusinessLogic(env_config=CONFIG)


@pytest.fixture
def core_with_preloaded_table() -> CoreBusinessLogic:
    duckdb = CoreBusinessLogic(env_config=CONFIG)
    path: str = "./data/president_polls_historical.csv"
    table_name: str = "president_polls_historical"
    duckdb.import_csv_file(path=path, table_ref=table_name)

    return duckdb


def test_export_table_to_parquet(core_with_preloaded_table: CoreBusinessLogic):
    table_name = "president_polls_historical"
    parquet_path = f"{TEST_TEMP_DIR}/automated-test-president-polls-historical-{int(time.time())}.parquet"

    assert not exists(parquet_path)

    core_with_preloaded_table.export_table_to_parquet(
        table_name=table_name,
        parquet_path=parquet_path
                                                     )

    assert exists(parquet_path)


def test_import_csv_to_in_memory_table(core: CoreBusinessLogic) -> None:
    path: str = "./data/president_polls.csv"
    table_name: str = "president_polls"

    core.import_csv_file(path=path, table_ref=table_name)

    # read back the table by querying it
    df = core.execute_as_df(query_str="select * from president_polls")
    assert len(df) > 100


def test_execute_as_df(core_with_preloaded_table: CoreBusinessLogic) -> None:
    query = f"""
        select
            pp.*
        from president_polls_historical pp
    """
    df = core_with_preloaded_table.execute_as_df(query_str=query)
    assert len(df) > 100


def test_execute_as_df_with_meta_data(core_with_preloaded_table) -> None:
    query = "select p.population, p.sample_size, p.sponsor_candidate, p.stage from president_polls_historical p"
    df, df_meta = core_with_preloaded_table.execute_as_df_with_meta_data(query_str=query)

    assert len(df) > 100
    assert "population" in df.columns
    assert "population" in df_meta["column_name"].tolist()


def test_map_to_duckdb_response(core_with_preloaded_table: CoreBusinessLogic) -> None:
    # NB: We assume this query works, and test mapping of this result. Testing of the query & meta data is tested
    #     elsewhere
    query = "select p.population, p.sample_size, p.sponsor_candidate, p.stage from president_polls_historical p"
    df_data, df_metadata = core_with_preloaded_table.execute_as_df_with_meta_data(query_str=query)

    response: DuckDbQueryResponse = core_with_preloaded_table.map_response(df_data=df_data, df_metadata=df_metadata)

    assert len(response.columns) == 4
    assert response.columns[0].name == "population"
    assert response.columns[1].name == "sample_size"
    assert response.columns[2].name == "sponsor_candidate"
    assert response.columns[3].name == "stage"


def test_process_new_csv_file_to_gcs_parquet(core: CoreBusinessLogic):
    path = "./data/president_polls_historical.csv"
    table_name: TableRef = "president_polls_historical"
    parquet_key = f"{table_name}.parquet"

    ref_group = core.process_new_csv_file_to_gcs_parquet(
        csv_path=path,
        table_name=table_name,
        parquet_key=parquet_key,
    )

    assert ref_group.ref == table_name
    assert ref_group.parquet_key == parquet_key
    assert ref_group.bucket_name == core.bucket_name

    # We should be able to download the new file, and save it to disk
    temp_dest_file = f"{TEST_TEMP_DIR}/{parquet_key}.roundtrip"
    if exists(temp_dest_file):
        os.remove(temp_dest_file)

    assert not exists(temp_dest_file)
    core.blob_storage.fetch_file(
        bucket_name=ref_group.bucket_name,
        key=ref_group.parquet_key,
        dest_path=temp_dest_file,
    )
    assert exists(temp_dest_file)

    # We should be able to query the new table
    df = core.execute_as_df(query_str=f"select * from {table_name}")
    assert len(df) > 1


def test_persist_then_fetch_ref_group(core: CoreBusinessLogic):
    ref_group = TableRefGroup.from_ref(
        table_ref=f"automated-test-{random.randint(0, 1_000_000)}",
        env_config=CONFIG
    )

    core.persist_ref_group(ref_group=ref_group)

    fetched_ref_group = core.fetch_ref_group_from_storage(
        ref=ref_group.ref,
    )

    assert ref_group == fetched_ref_group


def test_persist_ref_group_twice_overrides_quietly(core: CoreBusinessLogic):
    ref_group = TableRefGroup.from_ref(
        table_ref=f"automated-test-{random.randint(0, 1_000_000)}",
        env_config=CONFIG
    )

    core.persist_ref_group(ref_group=ref_group)

    # 2nd time without error implicitly tests the desired behavior for this test
    core.persist_ref_group(ref_group=ref_group)


def test_fetch_non_existent_ref_group_raises(core: CoreBusinessLogic):
    ref_group = TableRefGroup.from_ref(
        table_ref=f"non-existent-ref{random.randint(0, 1_000_000)}",
        env_config=CONFIG
    )

    with pytest.raises(Exception):
        _ = core.fetch_ref_group_from_storage(
            ref=ref_group.ref,
        )
