## Customer Insight Generator (Python + SQL + pandas/numpy/matplotlib)

This project generates marketing-ready customer insights from an SQL database (SQLite demo included) using Python with pandas, numpy, and matplotlib.

### Features
- RFM analysis: Recency, Frequency, Monetary value per customer, with quantile scoring
- Cohort retention analysis: Acquisition cohorts and month-over-month retention heatmap
- Order history trends: Orders and revenue over time
- CLI to run end-to-end: load data, compute insights, save CSVs and PNG charts
- Demo seeder to create a realistic SQLite database for quick start

### Quick start
1) Create a Python virtual environment (recommended)
```bash
python3 -m venv .venv && source .venv/bin/activate
```

2) Install requirements
```bash
pip install -r requirements.txt
```

3) Seed a demo SQLite database
```bash
python -m insights.seed_demo --db /tmp/customer_insights_demo.sqlite --customers 2000 --start "2022-01-01" --end "2025-09-30"
```

4) Run the insights pipeline (SQLite demo)
```bash
python -m insights.cli run-all --db /tmp/customer_insights_demo.sqlite --out ./outputs
```

Outputs include:
- CSVs: `rfm.csv`, `cohort_retention.csv`, `orders_over_time.csv`
- Charts: `rfm_histograms.png`, `cohort_retention_heatmap.png`, `orders_over_time.png`

### Database schema (demo)
The seeder creates minimal tables:
- `customers(customer_id INTEGER PRIMARY KEY, signup_date TEXT)`
- `orders(order_id INTEGER PRIMARY KEY, customer_id INTEGER, order_date TEXT, order_value REAL)`

You can adapt `insights/db.py` to your real schema; ensure `orders` contains at least: `customer_id`, `order_date`, and `order_value`.

### Run against a production SQL database (e.g., Douglas)
Provide a SQLAlchemy DSN and optionally map table/column names to your schema:
```bash
python -m insights.cli run-all \
  --dsn "postgresql+psycopg2://USER:PASS@HOST:5432/DBNAME" \
  --orders-table "orders" \
  --customers-table "customers" \
  --col-customer-id "customer_id" \
  --col-order-id "order_id" \
  --col-order-date "order_date" \
  --col-order-value "order_value" \
  --col-signup-date "signup_date" 
```

### CLI usage
```bash
python -m insights.cli --help
python -m insights.seed_demo --help
```

### Notes
- Uses only stdlib `sqlite3` for DB connectivity in the demo. For other SQL engines, replace the connection in `insights/db.py` and keep using `pandas.read_sql_query`.
- Charts are matplotlib-based and saved as PNGs.


