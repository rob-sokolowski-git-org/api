import duckdb
import pandas as pd
import random
import typing as t

from api.types import DuckDbQueryResponse, Column, TableRef, TableRefGroup
from env_config import EnvironmentConfig
from api import object_storage as obj



class CoreBusinessLogic:
    def __init__(self, env_config: EnvironmentConfig, blob_storage=obj):
        self._con: duckdb.DuckDBPyConnection = duckdb.connect(
            check_same_thread=False, # TODO: This might be a bad idea: https://github.com/rob-sokolowski-git-org/api/issues/12
        )
        self._bucket_name: str = env_config.bucket_name
        self._temp_dir: str = env_config.temp_dir
        self._blob_storage = blob_storage

        self._create_bucket_if_required()

    def _create_bucket_if_required(self):
        # TODO: Test case for this method
        try:
            self._blob_storage.get_bucket(self._bucket_name)
        except Exception as _:
            # TODO: Need to implement logging
            # TODO: Narrowing exception types in obj storage class
            # TODO: Should this be implied in upload file method? Maybe with a flag?
            self._blob_storage.create_bucket(self._bucket_name)

    @property
    def bucket_name(self) -> str:
        return self._bucket_name

    @property
    def blob_storage(self):
        return self._blob_storage

    @staticmethod
    def map_response(df_data: pd.DataFrame, df_metadata: pd.DataFrame) -> DuckDbQueryResponse:
        data_dict = df_data.to_dict(orient="list")
        metadata_records = df_metadata.to_dict(orient="records")

        columns = [Column(
                    name=record["column_name"],
                    type=record["column_type"],
                    values=data_dict[record["column_name"]]
                ) for record in metadata_records]

        return DuckDbQueryResponse(columns=columns)

    def import_csv_file(self, path: str, table_ref: TableRef):
        query_str = f"CREATE TABLE {table_ref} AS SELECT * FROM '{path}';"
        self._con.execute(query=query_str)

    def execute(self, query_str: str):  # return type intentionally omitted, let DuckDB handle the duck typing
        return self._con.execute(query=query_str)

    def execute_as_df(self, query_str: str) -> pd.DataFrame:
        return self.execute(query_str=query_str).df()

    def execute_as_df_with_meta_data(self, query_str) -> t.Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Workaround in an attempt to return info-schema data for front-end deserialization purposes

        Steps:
            1. disguise query as new randomly-named view
            2. select * from {the new view}
            3. describe {the new view}
            4. return Tuple of [step 2, step 3]

        Note: I haven't considered latency of this "view shuffle" at all
        """
        view_name = f"tmp_view_{random.randint(0, 10_000)}"
        view_cmd = f"""
            CREATE VIEW {view_name} as {query_str}
        """
        self.execute(query_str=view_cmd)
        df_data = self.execute_as_df(query_str=query_str)
        df_metadata = self.execute_as_df(query_str=f"describe {view_name}")

        return df_data, df_metadata

    def export_table_to_parquet(self, table_name: str, parquet_path: str):
        query_str = f"""
        COPY (SELECT * FROM {table_name}) TO '{parquet_path}' (FORMAT 'parquet');
        """
        self._con.execute(query=query_str)

    def process_new_csv_file_to_gcs_parquet(self, csv_path: str, table_name: TableRef) -> TableRefGroup:
        ref_group = TableRefGroup.from_ref(table_ref=table_name)

        self.import_csv_file(path=csv_path, table_ref=ref_group.ref)
        temp_parquet_path = f"{self._temp_dir}/{ref_group.parquet_key}"

        self.export_table_to_parquet(
            table_name=ref_group.ref,
            parquet_path=temp_parquet_path
        )

        self._blob_storage.create_file(
            path=temp_parquet_path,
            bucket_name=ref_group.bucket_name,
            key=ref_group.parquet_key,
        )

        return ref_group
