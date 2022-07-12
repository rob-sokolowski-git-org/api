import duckdb
import pandas as pd
import numpy as np
import random
import typing as t

from api.types import DuckDbQueryResponse, BaseColumn, TableRef, TableRefGroup, VarcharColumn, IntegerColumn, \
    DefaultColumn
from env_config import EnvironmentConfig
from api import object_storage as obj



class CoreBusinessLogic:
    def __init__(self, env_config: EnvironmentConfig, blob_storage=obj):
        self._con: duckdb.DuckDBPyConnection = duckdb.connect(
            check_same_thread=False, # TODO: This might be a bad idea..
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

        columns: t.List[BaseColumn] = []
        for record in metadata_records:
            match record["column_type"]:
                case "VARCHAR":
                    clazz = VarcharColumn
                case "INTEGER":
                    clazz = IntegerColumn
                case _:
                    clazz = DefaultColumn

            columns.append(clazz(
                        name=record["column_name"],
                        type=record["column_type"],
                        values=data_dict[record["column_name"]],
                    ))

        return DuckDbQueryResponse(columns=columns)

    def import_csv_file(self, path: str, table_ref: TableRef):
        query_str = f"CREATE TABLE {table_ref} AS SELECT * FROM read_csv_auto('{path}', auto_detect=True, all_varchar=True);"
        self._con.execute(query=query_str)

    def execute(self, query_str: str):  # return type intentionally omitted, let DuckDB handle the duck typing
        return self._con.execute(query=query_str)

    def execute_as_df(self, query_str: str) -> pd.DataFrame:
        e = self.execute(query_str=query_str)
        df: pd.DataFrame = e.df()
        df.replace({np.nan: ""}, inplace=True)
        return df

    def import_remote_parquet_to_memory(self, table_ref: TableRef):
        parquet_key = f"{table_ref}.parquet"
        temp_dest_path = f"{self._temp_dir}/{random.randint(0, 1_000_000)}.parquet"

        self.blob_storage.fetch_file(
            bucket_name=self.bucket_name,
            key=parquet_key,
            dest_path=temp_dest_path,
        )

        import_query_str = f"""
        CREATE TABLE {table_ref} as SELECT * FROM '{temp_dest_path}'
        """
        self.execute(query_str=import_query_str)


    def execute_as_df_with_meta_data(self,
                                     query_str: str,
                                     allow_blob_fallback: bool,
                                     fallback_tables: t.List[TableRef]
                                     ) -> t.Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Workaround in an attempt to return info-schema data for front-end deserialization purposes

        TODO: notes on fallback strategy

        Steps:
            1. disguise query as new randomly-named view
            2. select * from {the new view}
            3. describe {the new view}
            4. return Tuple of [step 2, step 3]

        Note: I haven't considered latency of this "view shuffle" at all
        """

        try:
            view_name = f"tmp_view_{random.randint(0, 10_000)}"
            view_cmd = f"""
                CREATE VIEW {view_name} as {query_str}
            """
            self.execute(query_str=view_cmd)
            df_data = self.execute_as_df(query_str=query_str)
            df_metadata = self.execute_as_df(query_str=f"describe {view_name}")
            return df_data, df_metadata
        except Exception as ex:
            if allow_blob_fallback is True:
                for table_ref in fallback_tables:
                    # TODO: a likely worthwhile async optimization possible here! https://github.com/rob-sokolowski-git-org/api/issues/13
                    self.import_remote_parquet_to_memory(table_ref=table_ref)

                    # Call this function again, this time without allowing fallback
                    return self.execute_as_df_with_meta_data(
                        query_str=query_str,
                        fallback_tables=[],
                        allow_blob_fallback=False)
            else:
                raise ex

    def export_table_to_parquet(self, table_name: str, parquet_path: str):
        query_str = f"""
        COPY (SELECT * FROM {table_name}) TO '{parquet_path}' (FORMAT 'parquet');
        """
        self._con.execute(query=query_str)

    def persist_ref_group(self, ref_group: TableRefGroup):
        """
        persists ref_group metadata to blob storage

        this is not intended for long term use, CockroachDB seems like the best
        pricing model for a hobbyist-tier relational DB

        https://github.com/rob-sokolowski-git-org/api/issues/16
        """
        temp_path = f"{self._temp_dir}/{ref_group.ref}.json"
        with open(temp_path, 'w') as f:
            f.write(ref_group.to_json())

        self._blob_storage.create_file(
            path=temp_path,
            bucket_name=self.bucket_name,
            key=ref_group.ref,
        )

    def fetch_ref_group_from_storage(self, ref: TableRef) -> TableRefGroup:
        """
        fetches ref_group, where `TableRef` is the blob key from blob storage

        this is not intended for long term use, CockroachDB seems like the best
        pricing model for a hobbyist-tier relational DB

        https://github.com/rob-sokolowski-git-org/api/issues/16
        """
        temp_dest_path = f"{self._temp_dir}/{ref}.json"

        self.blob_storage.fetch_file(
            bucket_name=self.bucket_name,
            key=ref,
            dest_path=temp_dest_path,
        )

        with open(temp_dest_path, 'r') as f:
            ref_group = TableRefGroup.from_json(f.read())
            return ref_group

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

        self.persist_ref_group(ref_group=ref_group)

        return ref_group

    def list_known_table_refs(self) -> t.List[TableRef]:
        """
        Ugly workaround for not having this info saved in a DB

        Assume:
            * we only have table_refs and parquet files
            * exclude all blobs with `.parquet` suffix

        When this assumption is no longer valid is when I think a proper DB solution is in order
        """
        blobs = self.blob_storage.list_blobs(self.bucket_name)
        return [b.name for b in blobs if not b.name.endswith(".parquet")]
