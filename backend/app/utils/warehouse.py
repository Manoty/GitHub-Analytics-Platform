# backend/app/utils/warehouse.py

import duckdb
import os
from typing import Any
from app.core.config import settings


class WarehouseManager:
    """
    Manages a persistent DuckDB connection.

    Architecture decision:
    - DuckDB is embedded — no server needed, zero infra cost.
    - We use the postgres_scanner extension to pull data directly from
      PostgreSQL into DuckDB columnar format on demand.
    - All heavy analytical aggregations run inside DuckDB, keeping
      PostgreSQL free for transactional workloads.
    - The warehouse file is persisted at DUCKDB_PATH so materialised
      views survive restarts.
    """

    _instance: "WarehouseManager | None" = None
    _conn: duckdb.DuckDBPyConnection | None = None

    def __new__(cls) -> "WarehouseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            os.makedirs(os.path.dirname(settings.duckdb_path), exist_ok=True)
            self._conn = duckdb.connect(settings.duckdb_path)
            self._bootstrap()
        return self._conn

    def _bootstrap(self) -> None:
        """Install extensions and load data from PostgreSQL on first connect."""
        conn = self._conn
        conn.execute("INSTALL postgres; LOAD postgres;")
        conn.execute("INSTALL json; LOAD json;")

        # Attach PostgreSQL as a foreign database
        pg_url = (
            f"host={settings.postgres_host} "
            f"port={settings.postgres_port} "
            f"dbname={settings.postgres_db} "
            f"user={settings.postgres_user} "
            f"password={settings.postgres_password}"
        )
        conn.execute(f"""
            ATTACH '{pg_url}' AS pg (TYPE postgres, READ_ONLY);
        """)

    def query(self, sql: str, params: list | None = None) -> list[dict[str, Any]]:
        """Execute a SQL query and return rows as list of dicts."""
        conn = self.get_connection()
        result = conn.execute(sql, params or [])
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def refresh_materialized(self, table_name: str, sql: str) -> None:
        """Drop and recreate a materialized DuckDB table from a query."""
        conn = self.get_connection()
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.execute(f"CREATE TABLE {table_name} AS {sql}")

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None


warehouse = WarehouseManager()