import time
from pathlib import Path
import polars as pl
from rich.console import Console
from src.config import settings
from src.warehouse.engine import warehouse
from src.warehouse.schema import initialize_gold_schema
from src.ingestion.synthetic_generator import generate_dimensions, generate_massive_fact_sales

console = Console()

class MedallionPipeline:
    """
    Executes the End-to-End Medallion Lakehouse Pipeline:
    Bronze (Raw Staging) -> Silver (Cleaned/Conformed Parquet) -> Gold (Kimball Star Schema in DuckDB).
    """
    def __init__(self):
        self.bronze_dir = settings.BRONZE_DIR
        self.silver_dir = settings.SILVER_DIR
        self.gold_dir = settings.GOLD_DIR

    def run_pipeline(self, n_rows: int = 1_000_000) -> dict:
        console.print(f"[bold magenta]▶ Starting Medallion Lakehouse Pipeline ({n_rows:,} records)...[/bold magenta]")
        start_time = time.time()
        
        # 1. BRONZE LAYER: Ingestion & Raw Staging
        t0 = time.time()
        console.print("[cyan][Bronze][/cyan] Generating dimensional entities and raw transactional events...")
        dims = generate_dimensions()
        fact_df = generate_massive_fact_sales(n_rows=n_rows, dims=dims)
        
        bronze_file = self.bronze_dir / "raw_events.parquet"
        fact_df.write_parquet(bronze_file, compression="snappy")
        bronze_duration = round(time.time() - t0, 3)
        console.print(f"[green]✔ Bronze completed in {bronze_duration}s ({bronze_file.stat().st_size / (1024*1024):.1f} MB)[/green]")

        # 2. SILVER LAYER: Validation, Cleansing & Conforming
        t1 = time.time()
        console.print("[cyan][Silver][/cyan] Cleansing, validating types, removing anomalies and conforming...")
        silver_df = pl.read_parquet(bronze_file)
        
        # Filter negative numbers or impossible states
        silver_df = silver_df.filter(
            (pl.col("quantity") > 0) & 
            (pl.col("net_revenue") >= 0) & 
            (pl.col("date_id").is_not_null())
        ).unique(subset=["transaction_id"])

        silver_file = self.silver_dir / "sales_conformed.parquet"
        silver_df.write_parquet(silver_file, compression="zstd")
        silver_duration = round(time.time() - t1, 3)
        console.print(f"[green]✔ Silver completed in {silver_duration}s ({silver_file.stat().st_size / (1024*1024):.1f} MB)[/green]")

        # 3. GOLD LAYER: Materialization into DuckDB Star Schema
        t2 = time.time()
        console.print("[cyan][Gold][/cyan] Materializing Kimball Star Schema and analytical views in DuckDB...")
        
        with warehouse.get_connection(read_only=False) as con:
            # Recreate schema
            initialize_gold_schema(con)
            
            # Load Dimensions
            for dim_name, dim_table in dims.items():
                con.register("tmp_dim", dim_table.to_arrow())
                con.execute(f"INSERT OR REPLACE INTO {dim_name} SELECT * FROM tmp_dim;")
                con.unregister("tmp_dim")
            
            # Load Facts directly from Silver Parquet with zero-copy vectorized scan
            con.execute(f"""
                INSERT OR REPLACE INTO fact_sales 
                SELECT * FROM read_parquet('{silver_file}');
            """)
            
        gold_duration = round(time.time() - t2, 3)
        total_duration = round(time.time() - start_time, 3)
        console.print(f"[green]✔ Gold completed in {gold_duration}s[/green]")
        console.print(f"[bold green]✔ Pipeline finished successfully in {total_duration}s total![/bold green]")

        return {
            "status": "success",
            "rows_processed": n_rows,
            "bronze_duration_sec": bronze_duration,
            "silver_duration_sec": silver_duration,
            "gold_duration_sec": gold_duration,
            "total_duration_sec": total_duration,
            "stats": warehouse.get_stats()
        }

pipeline = MedallionPipeline()
