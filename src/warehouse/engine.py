import duckdb
from pathlib import Path
from contextlib import contextmanager
from src.config import settings

class WarehouseEngine:
    """
    High-performance OLAP engine wrapping DuckDB.
    Provides vectorized execution, in-memory caching and persistent columnar storage.
    """
    def __init__(self, db_path: Path = settings.DUCKDB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        # Initialize connection settings
        self._init_db()

    def _init_db(self):
        """Configure DuckDB pragmas for maximum throughput on multi-core Linux systems."""
        with self.get_connection() as con:
            con.execute("PRAGMA threads=8;")
            con.execute("PRAGMA memory_limit='4GB';")
            con.execute("PRAGMA preserve_insertion_order=false;")

    @contextmanager
    def get_connection(self, read_only: bool = False):
        """Context manager for thread-safe DuckDB connection access."""
        con = duckdb.connect(database=str(self.db_path), read_only=read_only)
        try:
            yield con
        finally:
            con.close()

    def execute_query(self, sql: str, params: list = None) -> list[dict]:
        """Execute a read query and return records as a list of dictionaries."""
        with self.get_connection(read_only=True) as con:
            rel = con.execute(sql, params or [])
            columns = [desc[0] for desc in rel.description] if rel.description else []
            rows = rel.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def execute_query_arrow(self, sql: str, params: list = None):
        """Execute a query and return an Apache Arrow Table for zero-copy operations."""
        with self.get_connection(read_only=True) as con:
            return con.execute(sql, params or []).fetch_arrow_table()

    def get_stats(self) -> dict:
        """Return total row counts and storage metrics across the Lakehouse."""
        with self.get_connection(read_only=True) as con:
            tables = con.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main';"
            ).fetchall()
            
            table_stats = {}
            total_rows = 0
            for (t_name,) in tables:
                cnt = con.execute(f"SELECT COUNT(*) FROM {t_name};").fetchone()[0]
                table_stats[t_name] = cnt
                if t_name.startswith("fact_"):
                    total_rows += cnt

            db_size_bytes = self.db_path.stat().st_size if self.db_path.exists() else 0
            
            return {
                "tables": table_stats,
                "total_fact_rows": total_rows,
                "db_size_mb": round(db_size_bytes / (1024 * 1024), 2),
                "db_path": str(self.db_path)
            }

warehouse = WarehouseEngine()
