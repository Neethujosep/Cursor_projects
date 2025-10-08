from __future__ import annotations

import argparse
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np


def daterange(start_date: datetime, end_date: datetime):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(days=n)


def create_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            signup_date TEXT
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            order_value REAL,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
        );
        """
    )
    conn.commit()


def seed_demo(db_path: str, num_customers: int, start: str, end: str, seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)

    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)

    conn = sqlite3.connect(db_path)
    try:
        create_schema(conn)
        cur = conn.cursor()

        # Create customers with random signup dates across [start, end]
        days = (end_dt - start_dt).days
        signup_offsets = np.random.randint(0, max(days, 1), size=num_customers)
        signup_dates = [start_dt + timedelta(days=int(o)) for o in signup_offsets]

        cur.executemany(
            "INSERT INTO customers(customer_id, signup_date) VALUES (?, ?)",
            [(i + 1, d.date().isoformat()) for i, d in enumerate(signup_dates)],
        )

        # Orders: per customer, draw a Poisson number of orders, distribute over time
        order_id = 1
        for cid, signup in enumerate(signup_dates, start=1):
            # Expected orders scale with tenure
            tenure_days = max((end_dt - signup).days, 1)
            lam = min(tenure_days / 60.0, 10.0)  # more tenure => more expected orders
            num_orders = np.random.poisson(lam=lam)
            if num_orders <= 0:
                continue
            order_days = np.random.randint(0, tenure_days, size=num_orders)
            order_days.sort()
            for od in order_days:
                odt = signup + timedelta(days=int(od))
                if odt > end_dt:
                    continue
                value = float(np.round(np.random.lognormal(mean=3.2, sigma=0.6), 2))
                cur.execute(
                    "INSERT INTO orders(order_id, customer_id, order_date, order_value) VALUES (?, ?, ?, ?)",
                    (order_id, cid, odt.date().isoformat(), value),
                )
                order_id += 1

        conn.commit()
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed a demo SQLite database for customer insights")
    parser.add_argument("--db", required=True, help="Path to SQLite DB file to create")
    parser.add_argument("--customers", type=int, default=1000, help="Number of customers")
    parser.add_argument("--start", required=True, help="Start date ISO (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date ISO (YYYY-MM-DD)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    seed_demo(args.db, args.customers, args.start, args.end, args.seed)


if __name__ == "__main__":
    main()


