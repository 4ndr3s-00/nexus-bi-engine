"""
Kimball Star Schema DDL definitions for Gold Layer in DuckDB.
Enforces typed schemas, constraints, and analytical indexing.
"""

DDL_DIM_DATE = """
CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR NOT NULL,
    is_weekend BOOLEAN NOT NULL
);
"""

DDL_DIM_PRODUCT = """
CREATE TABLE IF NOT EXISTS dim_product (
    product_id INTEGER PRIMARY KEY,
    sku VARCHAR NOT NULL,
    product_name VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    subcategory VARCHAR NOT NULL,
    base_cost DOUBLE NOT NULL,
    list_price DOUBLE NOT NULL,
    target_margin_pct DOUBLE NOT NULL
);
"""

DDL_DIM_CUSTOMER = """
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR NOT NULL,
    segment VARCHAR NOT NULL,
    region VARCHAR NOT NULL,
    country VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    loyalty_tier VARCHAR NOT NULL
);
"""

DDL_DIM_CHANNEL = """
CREATE TABLE IF NOT EXISTS dim_channel (
    channel_id INTEGER PRIMARY KEY,
    channel_name VARCHAR NOT NULL,
    platform_type VARCHAR NOT NULL,
    fee_pct DOUBLE NOT NULL
);
"""

DDL_FACT_SALES = """
CREATE TABLE IF NOT EXISTS fact_sales (
    transaction_id BIGINT PRIMARY KEY,
    date_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DOUBLE NOT NULL,
    discount_pct DOUBLE NOT NULL,
    gross_amount DOUBLE NOT NULL,
    discount_amount DOUBLE NOT NULL,
    net_revenue DOUBLE NOT NULL,
    cost_amount DOUBLE NOT NULL,
    profit_margin DOUBLE NOT NULL,
    profit_margin_pct DOUBLE NOT NULL
);
"""

DDL_VIEWS = """
CREATE OR REPLACE VIEW gold_daily_kpis AS
SELECT
    d.full_date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    COUNT(f.transaction_id) AS total_orders,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.gross_amount), 2) AS total_gross_amount,
    ROUND(SUM(f.net_revenue), 2) AS total_net_revenue,
    ROUND(SUM(f.cost_amount), 2) AS total_cost_amount,
    ROUND(SUM(f.profit_margin), 2) AS total_profit,
    ROUND(SUM(f.profit_margin) / NULLIF(SUM(f.net_revenue), 0) * 100, 2) AS overall_margin_pct,
    ROUND(AVG(f.net_revenue), 2) AS average_order_value
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY 1, 2, 3, 4, 5;

CREATE OR REPLACE VIEW gold_category_regional_performance AS
SELECT
    d.year,
    d.quarter,
    p.category,
    p.subcategory,
    c.region,
    c.segment,
    COUNT(f.transaction_id) AS total_transactions,
    ROUND(SUM(f.net_revenue), 2) AS net_revenue,
    ROUND(SUM(f.profit_margin), 2) AS total_profit,
    ROUND(SUM(f.profit_margin) / NULLIF(SUM(f.net_revenue), 0) * 100, 2) AS profit_margin_pct
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY 1, 2, 3, 4, 5, 6;
"""

def initialize_gold_schema(con):
    """Executes all DDL and views to build the star schema in Gold layer."""
    con.execute(DDL_DIM_DATE)
    con.execute(DDL_DIM_PRODUCT)
    con.execute(DDL_DIM_CUSTOMER)
    con.execute(DDL_DIM_CHANNEL)
    con.execute(DDL_FACT_SALES)
    con.execute(DDL_VIEWS)
