import duckdb
import pandas as pd
import numpy as np


class DuckCore:
    def __init__(self):
        self._con: duckdb.DuckDBPyConnection = duckdb.connect()

    def import_csv_file(self, path: str, table_name: str):
        query_str = f"""
        CREATE TABLE {table_name} AS SELECT * FROM '{path}';
        """
        self._con.execute(query=query_str)

    def execute_as_df(self, query_str: str) -> pd.DataFrame:
        return self._con.execute(query=query_str).df()
