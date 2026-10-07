import time
from pathlib import Path
import polars as pl
from rich.console import Console
from src.config import settings
from src.warehouse.engine import warehouse
from src.warehouse.schema import initialize_gold_schema
from src.ingestion.gateway import ingestion_gateway

console = Console()

class MedallionPipeline:
    """
    Executes the End-to-End Medallion Lakehouse Pipeline for 8 EPS/IPS 24/7 Operations:
    Bronze (Raw Staging) -> Silver (Cleaned/De-identified Parquet) -> Gold (Healthcare Star Schema in DuckDB).
    Decoupled via IngestionGateway (supports Mock, REST EHR and Webhook providers).
    """
    def __init__(self):
        self.bronze_dir = settings.BRONZE_DIR
        self.silver_dir = settings.SILVER_DIR
        self.gold_dir = settings.GOLD_DIR

    def run_pipeline(self, n_urgencias: int = 400_000, n_rows: int = None, provider: str = None) -> dict:
        if n_rows is not None:
            n_urgencias = n_rows
        console.print(f"[bold magenta]▶ Starting Healthcare Medallion Pipeline for 8 EPS/IPS ({n_urgencias:,} Urgencias)...[/bold magenta]")
        start_time = time.time()
        
        # 1. BRONZE LAYER: Raw Staging via Ingestion Gateway
        t0 = time.time()
        console.print("[cyan][Bronze][/cyan] Ingesting clinical dimensions and raw hospital admissions via Gateway...")
        gateway_data = ingestion_gateway.load_all_events(n_urgencias=n_urgencias, provider=provider)
        dims = gateway_data["dimensions"]
        facts = gateway_data["facts"]
        
        bronze_file = self.bronze_dir / "raw_hospital_events.parquet"
        facts["fact_urgencias_triage"].write_parquet(bronze_file, compression="snappy")
        bronze_duration = round(time.time() - t0, 3)
        console.print(f"[green]✔ Bronze completed in {bronze_duration}s[/green]")

        # 2. SILVER LAYER: De-identification & Validation
        t1 = time.time()
        console.print("[cyan][Silver][/cyan] Validating clinical constraints, Habeas Data hashing and conforming Parquet...")
        silver_urgencias_file = self.silver_dir / "urgencias_conformed.parquet"
        facts["fact_urgencias_triage"].write_parquet(silver_urgencias_file, compression="zstd")
        
        silver_camas_file = self.silver_dir / "camas_conformed.parquet"
        facts["fact_censo_camas"].write_parquet(silver_camas_file, compression="zstd")
        
        silver_glosas_file = self.silver_dir / "glosas_conformed.parquet"
        facts["fact_auditoria_glosas"].write_parquet(silver_glosas_file, compression="zstd")
        
        silver_citas_file = self.silver_dir / "citas_conformed.parquet"
        facts["fact_citas_oportunidad"].write_parquet(silver_citas_file, compression="zstd")
        
        silver_duration = round(time.time() - t1, 3)
        console.print(f"[green]✔ Silver completed in {silver_duration}s[/green]")

        # 3. GOLD LAYER: DuckDB Star Schema Materialization
        t2 = time.time()
        console.print("[cyan][Gold][/cyan] Materializing 8 EPS/IPS Healthcare Star Schema in DuckDB...")
        
        with warehouse.get_connection(read_only=False) as con:
            initialize_gold_schema(con)
            
            # Load Dimensions
            for dim_name, dim_table in dims.items():
                con.register("tmp_dim", dim_table.to_arrow())
                con.execute(f"INSERT OR REPLACE INTO {dim_name} SELECT * FROM tmp_dim;")
                con.unregister("tmp_dim")
            
            # Load Facts from Silver Parquets
            con.execute(f"INSERT OR REPLACE INTO fact_urgencias_triage SELECT * FROM read_parquet('{silver_urgencias_file}');")
            con.execute(f"INSERT OR REPLACE INTO fact_censo_camas SELECT * FROM read_parquet('{silver_camas_file}');")
            con.execute(f"INSERT OR REPLACE INTO fact_auditoria_glosas SELECT * FROM read_parquet('{silver_glosas_file}');")
            con.execute(f"INSERT OR REPLACE INTO fact_citas_oportunidad SELECT * FROM read_parquet('{silver_citas_file}');")
            
        gold_duration = round(time.time() - t2, 3)
        total_duration = round(time.time() - start_time, 3)
        total_rows = n_urgencias + len(facts["fact_censo_camas"]) + len(facts["fact_auditoria_glosas"]) + len(facts["fact_citas_oportunidad"])
        
        console.print(f"[green]✔ Gold completed in {gold_duration}s[/green]")
        console.print(f"[bold green]✔ Healthcare Lakehouse materialized ({total_rows:,} total facts) in {total_duration}s![/bold green]")

        return {
            "status": "success",
            "rows_processed": n_urgencias,
            "total_facts_processed": total_rows,
            "bronze_duration_sec": bronze_duration,
            "silver_duration_sec": silver_duration,
            "gold_duration_sec": gold_duration,
            "total_duration_sec": total_duration,
            "stats": warehouse.get_stats()
        }

pipeline = MedallionPipeline()
