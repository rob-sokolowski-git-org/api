import duckdb
import pandas as pd
import random
import typing as t

from api.types import DuckDbQueryResponse, Column
from env_config import EnvironmentConfig


class DuckRapper:
    """https://www.youtube.com/watch?v=6_BGKyAKigs"""

    def __init__(self, env_config: EnvironmentConfig):
        self._con: duckdb.DuckDBPyConnection = duckdb.connect()
        self._bucket_name: str = env_config.bucket_name

    @property
    def bucket_name(self) -> str:
        return self._bucket_name

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

    def import_csv_file(self, path: str, table_name: str):
        query_str = f"CREATE TABLE {table_name} AS SELECT * FROM '{path}';"
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
