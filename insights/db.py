from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator, Optional, Union

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@contextmanager
def connect_sqlite(sqlite_path: str) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(sqlite_path, detect_types=sqlite3.PARSE_DECLTYPES)
    try:
        yield conn
    finally:
        conn.close()


def create_sql_engine(dsn: str) -> Engine:
    """
    Create a SQLAlchemy Engine from a DSN like:
    - postgresql+psycopg2://user:pass@host:5432/dbname
    - mssql+pyodbc://user:pass@host:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server
    - mysql+pymysql://user:pass@host:3306/dbname
    - sqlite:////absolute/path/to/db.sqlite
    """
    return create_engine(dsn, pool_pre_ping=True)


def load_orders(
    conn: Union[sqlite3.Connection, Engine],
    orders_table: str = "orders",
    customers_table: Optional[str] = None,
    col_customer_id: str = "customer_id",
    col_order_id: str = "order_id",
    col_order_date: str = "order_date",
    col_order_value: str = "order_value",
    col_signup_date: str = "signup_date",
) -> pd.DataFrame:
    """
    Load orders into a DataFrame. Expected columns: customer_id, order_date, order_value.
    If customers_table is provided, it will LEFT JOIN to enrich with signup_date if present.
    """
    if customers_table:
        query = f"""
            SELECT o.{col_order_id} AS order_id,
                   o.{col_customer_id} AS customer_id,
                   o.{col_order_date} AS order_date,
                   o.{col_order_value} AS order_value,
                   c.{col_signup_date} AS signup_date
            FROM {orders_table} o
            LEFT JOIN {customers_table} c ON o.{col_customer_id} = c.{col_customer_id}
        """
    else:
        query = f"""
            SELECT {col_order_id} AS order_id,
                   {col_customer_id} AS customer_id,
                   {col_order_date} AS order_date,
                   {col_order_value} AS order_value
            FROM {orders_table}
        """

    df = pd.read_sql_query(query, conn)
    # Normalize dtypes
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], utc=False, errors="coerce")
    if "signup_date" in df.columns:
        df["signup_date"] = pd.to_datetime(df["signup_date"], utc=False, errors="coerce")
    if "order_value" in df.columns:
        df["order_value"] = pd.to_numeric(df["order_value"], errors="coerce")
    return df


