import time
from rich.console import Console
from rich.table import Table
from src.ingestion.pipeline import pipeline
from src.warehouse.engine import warehouse

console = Console()

def run_1m_benchmark():
    console.print("[bold cyan]═════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]   🚀 BENCHMARK DE RENDIMIENTO: 1,000,000 REGISTROS OLAP   [/bold cyan]")
    console.print("[bold cyan]═════════════════════════════════════════════════════════════[/bold cyan]")

    # Run full ingestion of 1,000,000 records
    res = pipeline.run_pipeline(n_rows=1_000_000)
    
    # Run test queries
    queries = [
        (
            "Agregación Total de Ventas y Márgenes (1M filas)",
            """
            SELECT 
                COUNT(*) AS total_tx,
                ROUND(SUM(net_revenue), 2) AS total_revenue,
                ROUND(SUM(profit_margin), 2) AS total_profit,
                ROUND(AVG(profit_margin_pct), 2) AS avg_margin
            FROM fact_sales;
            """
        ),
        (
            "Corte Trimestral por Categoría y Región (Multi-JOIN 4 Tablas)",
            """
            SELECT
                d.year,
                d.quarter,
                p.category,
                c.region,
                COUNT(f.transaction_id) AS orders,
                ROUND(SUM(f.net_revenue), 2) AS revenue,
                ROUND(SUM(f.profit_margin), 2) AS profit
            FROM fact_sales f
            JOIN dim_date d ON f.date_id = d.date_id
            JOIN dim_product p ON f.product_id = p.product_id
            JOIN dim_customer c ON f.customer_id = c.customer_id
            WHERE d.year = 2025
            GROUP BY 1, 2, 3, 4
            ORDER BY revenue DESC
            LIMIT 10;
            """
        ),
        (
            "Filtro Avanzado Top 5 Clientes con Window Function",
            """
            SELECT 
                c.customer_name,
                c.segment,
                c.region,
                ROUND(SUM(f.net_revenue), 2) AS total_spent,
                RANK() OVER (ORDER BY SUM(f.net_revenue) DESC) AS rank
            FROM fact_sales f
            JOIN dim_customer c ON f.customer_id = c.customer_id
            GROUP BY c.customer_name, c.segment, c.region
            LIMIT 5;
            """
        )
    ]

    table = Table(title="Resultados del Benchmark en DuckDB (1M+ Registros)")
    table.add_column("Consulta Analítica", style="cyan")
    table.add_column("Filas Procesadas", style="magenta")
    table.add_column("Latencia (ms)", style="green bold")
    table.add_column("SLA Cumplido (<100ms)", style="yellow")

    for q_name, sql in queries:
        t0 = time.perf_counter()
        rows = warehouse.execute_query(sql)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        sla_pass = "✔ PASS (<100ms)" if elapsed_ms < 100 else "✘ FAIL"
        table.add_row(q_name, "1,000,000", f"{elapsed_ms:.2f} ms", sla_pass)

    console.print(table)

if __name__ == "__main__":
    run_1m_benchmark()
