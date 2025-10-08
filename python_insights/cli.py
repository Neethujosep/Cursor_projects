from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .db import connect_sqlite, load_orders, create_sql_engine
from .analytics import compute_rfm, compute_cohort_retention, compute_orders_over_time
from .viz import plot_rfm_histograms, plot_cohort_retention_heatmap, plot_orders_over_time


def run_all(db_path: str = None, out_dir: str = "./outputs", dsn: str = None,
            orders_table: str = "orders", customers_table: str = "customers",
            col_customer_id: str = "customer_id", col_order_id: str = "order_id",
            col_order_date: str = "order_date", col_order_value: str = "order_value",
            col_signup_date: str = "signup_date") -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    if dsn:
        engine = create_sql_engine(dsn)
        orders = load_orders(engine, orders_table=orders_table, customers_table=customers_table,
                             col_customer_id=col_customer_id, col_order_id=col_order_id,
                             col_order_date=col_order_date, col_order_value=col_order_value,
                             col_signup_date=col_signup_date)
    else:
        with connect_sqlite(db_path) as conn:
            orders = load_orders(conn, orders_table=orders_table, customers_table=customers_table,
                                 col_customer_id=col_customer_id, col_order_id=col_order_id,
                                 col_order_date=col_order_date, col_order_value=col_order_value,
                                 col_signup_date=col_signup_date)

    rfm = compute_rfm(orders)
    rfm.to_csv(out / "rfm.csv", index=False)
    plot_rfm_histograms(rfm, out / "rfm_histograms.png")

    cohorts = compute_cohort_retention(orders)
    cohorts.to_csv(out / "cohort_retention.csv")
    plot_cohort_retention_heatmap(cohorts, out / "cohort_retention_heatmap.png")

    oot = compute_orders_over_time(orders, freq="M")
    oot.to_csv(out / "orders_over_time.csv", index=False)
    plot_orders_over_time(oot, out / "orders_over_time.png")


def main() -> None:
    parser = argparse.ArgumentParser(description="Customer Insight Generator")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run-all", help="Run full insights pipeline")
    src = run.add_mutually_exclusive_group(required=True)
    src.add_argument("--db", help="Path to SQLite database")
    src.add_argument("--dsn", help="SQLAlchemy DSN for production DB (e.g., postgres://...)")
    run.add_argument("--out", required=True, help="Output directory for CSVs and charts")
    run.add_argument("--orders-table", default="orders")
    run.add_argument("--customers-table", default="customers")
    run.add_argument("--col-customer-id", default="customer_id")
    run.add_argument("--col-order-id", default="order_id")
    run.add_argument("--col-order-date", default="order_date")
    run.add_argument("--col-order-value", default="order_value")
    run.add_argument("--col-signup-date", default="signup_date")

    args = parser.parse_args()

    if args.command == "run-all":
        run_all(db_path=args.db, out_dir=args.out, dsn=args.dsn,
                orders_table=args.orders_table, customers_table=args.customers_table,
                col_customer_id=args.col_customer_id, col_order_id=args.col_order_id,
                col_order_date=args.col_order_date, col_order_value=args.col_order_value,
                col_signup_date=args.col_signup_date)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


