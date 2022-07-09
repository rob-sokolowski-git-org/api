2022-07-09:
 * rough sketch of a CloudRun, DuckDB, GCS, parquet deployment for datawarehousing on the cheap is running with decent integration test coverage
 * ran into issues attempting to install `google-cloud-firestore`, in retrospect I'm happy about this. I had decided awhile back to use CockroachDB, and am going to go with that
 * In the immediate term, I'll continue to use blob storage until querying is required. For now, I only need key-value lookups / storage, and blob storage will suffice (but be slow)

