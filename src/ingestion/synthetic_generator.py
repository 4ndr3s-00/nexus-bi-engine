import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import date, timedelta
import random
from pathlib import Path
from src.config import settings

def generate_dimensions() -> dict[str, pl.DataFrame]:
    """Generate realistic dimension tables for Kimball star schema."""
    
    # 1. dim_date (730 days = 2 years)
    start_date = date(2025, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(730)]
    
    dim_date = pl.DataFrame({
        "date_id": [int(d.strftime("%Y%m%d")) for d in dates],
        "full_date": dates,
        "year": [d.year for d in dates],
        "quarter": [(d.month - 1) // 3 + 1 for d in dates],
        "month": [d.month for d in dates],
        "month_name": [d.strftime("%B") for d in dates],
        "week_of_year": [d.isocalendar()[1] for d in dates],
        "day_of_month": [d.day for d in dates],
        "day_of_week": [d.isoweekday() for d in dates],
        "day_name": [d.strftime("%A") for d in dates],
        "is_weekend": [d.isoweekday() in (6, 7) for d in dates],
    })

    # 2. dim_product (500 enterprise tech products across 6 major sectors)
    categories = {
        "Cloud Infrastructure": ["Compute Nodes", "Object Storage", "Load Balancers", "Kubernetes Clusters"],
        "AI & Intelligence": ["LLM Inference API", "Vector Embeddings", "Model Fine-tuning", "Autonomous Agents"],
        "CyberSecurity": ["Zero Trust Gateway", "SIEM Analytics", "Identity Fabric", "Endpoint Guard"],
        "Data Engineering": ["Lakehouse Storage", "Streaming Pipeline", "ETL Compute", "Catalog Engine"],
        "Enterprise SaaS": ["CRM Suite", "ERP Core", "Billing Engine", "Compliance Tracker"],
        "Developer Platform": ["CI/CD Runners", "Dev Environments", "API Management", "Observability APM"],
    }
    
    prod_ids = []
    skus = []
    names = []
    cats = []
    subcats = []
    base_costs = []
    list_prices = []
    margins = []
    
    p_id = 1
    for cat, subs in categories.items():
        for sub in subs:
            for item_idx in range(1, 21):  # ~20 products per subcategory
                prod_ids.append(p_id)
                skus.append(f"SKU-{cat[:3].upper()}-{sub[:3].upper()}-{item_idx:03d}")
                names.append(f"{sub} Tier-{item_idx}")
                cats.append(cat)
                subcats.append(sub)
                
                cost = round(random.uniform(50.0, 1500.0), 2)
                markup = random.uniform(1.25, 2.50)
                price = round(cost * markup, 2)
                margin_pct = round(((price - cost) / price) * 100, 2)
                
                base_costs.append(cost)
                list_prices.append(price)
                margins.append(margin_pct)
                p_id += 1

    dim_product = pl.DataFrame({
        "product_id": prod_ids,
        "sku": skus,
        "product_name": names,
        "category": cats,
        "subcategory": subcats,
        "base_cost": base_costs,
        "list_price": list_prices,
        "target_margin_pct": margins,
    })

    # 3. dim_customer (2,000 corporate accounts)
    regions = ["North America", "Europe", "LATAM", "Asia-Pacific", "Middle East"]
    segments = ["Enterprise Global", "Mid-Market", "Scale-Up", "Public Sector"]
    loyalty_tiers = ["Platinum Partner", "Gold Core", "Silver Essential", "Standard"]
    
    c_ids = list(range(1, 2001))
    dim_customer = pl.DataFrame({
        "customer_id": c_ids,
        "customer_name": [f"Corp Global #{cid:04d}" for cid in c_ids],
        "segment": [random.choice(segments) for _ in c_ids],
        "region": [random.choice(regions) for _ in c_ids],
        "country": ["United States" if cid % 2 == 0 else "Germany" for cid in c_ids],
        "city": ["San Francisco" if cid % 2 == 0 else "Berlin" for cid in c_ids],
        "loyalty_tier": [random.choice(loyalty_tiers) for _ in c_ids],
    })

    # 4. dim_channel
    dim_channel = pl.DataFrame({
        "channel_id": [1, 2, 3, 4],
        "channel_name": ["Direct Enterprise Sales", "Cloud Marketplace", "Global Partner Network", "Self-Serve Portal"],
        "platform_type": ["B2B Direct", "Cloud Hyperscaler", "Indirect Reseller", "Digital Inbound"],
        "fee_pct": [0.02, 0.15, 0.08, 0.03],
    })

    return {
        "dim_date": dim_date,
        "dim_product": dim_product,
        "dim_customer": dim_customer,
        "dim_channel": dim_channel,
    }


def generate_massive_fact_sales(
    n_rows: int = 1_000_000,
    dims: dict[str, pl.DataFrame] = None
) -> pl.DataFrame:
    """
    Generate n_rows of transactional fact records in ultra-fast vectorized batches.
    Utilizes Polars columnar array expressions for sub-second generation.
    """
    if dims is None:
        dims = generate_dimensions()

    date_ids = dims["dim_date"]["date_id"].to_list()
    prod_ids = dims["dim_product"]["product_id"].to_list()
    cust_ids = dims["dim_customer"]["customer_id"].to_list()
    channel_ids = dims["dim_channel"]["channel_id"].to_list()

    # Create mapping array for product prices & costs to join vectorially
    p_df = dims["dim_product"].select(["product_id", "base_cost", "list_price"])

    # Base random columns generated with Polars expressions
    df = pl.DataFrame({
        "transaction_id": pl.int_range(1, n_rows + 1, dtype=pl.Int64, eager=True),
        "date_id": [random.choice(date_ids) for _ in range(n_rows)],
        "product_id": [random.choice(prod_ids) for _ in range(n_rows)],
        "customer_id": [random.choice(cust_ids) for _ in range(n_rows)],
        "channel_id": [random.choice(channel_ids) for _ in range(n_rows)],
        "quantity": [random.randint(1, 25) for _ in range(n_rows)],
        "discount_pct": [round(random.choice([0.0, 0.05, 0.10, 0.15, 0.20, 0.25]), 2) for _ in range(n_rows)],
    })

    # Join product financial properties vectorially
    df = df.join(p_df, on="product_id", how="left")

    # Compute financial metrics vectorially
    df = df.with_columns([
        pl.col("list_price").alias("unit_price"),
        (pl.col("quantity") * pl.col("list_price")).round(2).alias("gross_amount"),
        (pl.col("quantity") * pl.col("list_price") * pl.col("discount_pct")).round(2).alias("discount_amount"),
    ])

    df = df.with_columns([
        (pl.col("gross_amount") - pl.col("discount_amount")).round(2).alias("net_revenue"),
        (pl.col("quantity") * pl.col("base_cost")).round(2).alias("cost_amount"),
    ])

    df = df.with_columns([
        (pl.col("net_revenue") - pl.col("cost_amount")).round(2).alias("profit_margin"),
        (((pl.col("net_revenue") - pl.col("cost_amount")) / pl.col("net_revenue")) * 100).round(2).alias("profit_margin_pct"),
    ])

    # Select exact columns for fact_sales
    return df.select([
        "transaction_id",
        "date_id",
        "product_id",
        "customer_id",
        "channel_id",
        "quantity",
        "unit_price",
        "discount_pct",
        "gross_amount",
        "discount_amount",
        "net_revenue",
        "cost_amount",
        "profit_margin",
        "profit_margin_pct"
    ])
