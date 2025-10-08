from __future__ import annotations

import numpy as np
import pandas as pd


def compute_rfm(orders: pd.DataFrame, as_of_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """
    Compute RFM metrics per customer.
    - Recency: days since last order (lower is better)
    - Frequency: number of orders
    - Monetary: total spend
    Also adds quantile-based scores (1-5) for each dimension and a combined RFM score string.
    """
    if orders.empty:
        return pd.DataFrame(columns=[
            "customer_id", "recency_days", "frequency", "monetary",
            "r_score", "f_score", "m_score", "rfm_segment"
        ])

    orders = orders.dropna(subset=["customer_id", "order_date", "order_value"]).copy()
    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
    as_of = pd.to_datetime(as_of_date) if as_of_date is not None else orders["order_date"].max()

    agg = orders.groupby("customer_id").agg(
        last_order_date=("order_date", "max"),
        frequency=("order_id", "count"),
        monetary=("order_value", "sum"),
    ).reset_index()
    agg["recency_days"] = (as_of - agg["last_order_date"]).dt.days.astype("Int64")

    # Quantile scores: Recency lower is better; Frequency/Monetary higher is better
    def quantile_score(series: pd.Series, bins: int = 5, reverse: bool = False) -> pd.Series:
        # Handle edge case with constant values
        if series.nunique(dropna=True) <= 1:
            return pd.Series(np.full(len(series), 3, dtype=int), index=series.index)
        ranks = pd.qcut(series.rank(method="first"), bins, labels=False) + 1
        scores = ranks.astype(int)
        return (bins + 1 - scores) if reverse else scores

    agg["r_score"] = quantile_score(agg["recency_days"], reverse=True)
    agg["f_score"] = quantile_score(agg["frequency"], reverse=False)
    agg["m_score"] = quantile_score(agg["monetary"], reverse=False)
    agg["rfm_segment"] = agg["r_score"].astype(str) + agg["f_score"].astype(str) + agg["m_score"].astype(str)

    cols = ["customer_id", "recency_days", "frequency", "monetary", "r_score", "f_score", "m_score", "rfm_segment"]
    return agg[cols].sort_values(["r_score", "f_score", "m_score"], ascending=[False, False, False])


def compute_cohort_retention(orders: pd.DataFrame) -> pd.DataFrame:
    """
    Build acquisition cohorts by customer first order month and compute retention by months since acquisition.
    Returns a matrix-style DataFrame where rows=cohort_month, columns=period_number, values=retention_rate (0-1).
    """
    if orders.empty:
        return pd.DataFrame()

    df = orders.dropna(subset=["customer_id", "order_date"]).copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["order_month"] = df["order_date"].values.astype("datetime64[M]")

    # First purchase month per customer
    first_purchase = df.groupby("customer_id")["order_month"].min().rename("cohort_month")
    df = df.join(first_purchase, on="customer_id")

    # Period number: months since cohort month
    def months_between(a: pd.Series, b: pd.Series) -> pd.Series:
        return (a.dt.year - b.dt.year) * 12 + (a.dt.month - b.dt.month)

    df["period_number"] = months_between(df["order_month"].dt.to_period("M").dt.to_timestamp(),
                                          df["cohort_month"].dt.to_period("M").dt.to_timestamp())

    # Active customers in each cohort-period
    cohort_sizes = df.groupby("cohort_month")["customer_id"].nunique().rename("cohort_size")
    active_counts = df.groupby(["cohort_month", "period_number"])["customer_id"].nunique().rename("active_customers")
    retention = active_counts.to_frame().join(cohort_sizes, on="cohort_month")
    retention["retention"] = retention["active_customers"] / retention["cohort_size"]

    # Pivot to matrix form
    matrix = retention.reset_index().pivot(index="cohort_month", columns="period_number", values="retention").fillna(0.0)
    # Sort by cohort_month ascending
    matrix = matrix.sort_index()
    return matrix


def compute_orders_over_time(orders: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    """
    Aggregate orders and revenue over time at the provided frequency (e.g., 'D', 'W', 'M').
    Returns columns: period, num_orders, revenue.
    """
    if orders.empty:
        return pd.DataFrame(columns=["period", "num_orders", "revenue"])

    df = orders.dropna(subset=["order_date", "order_value"]).copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df.set_index("order_date", inplace=True)
    grouped = df.resample(freq).agg({"order_id": "count", "order_value": "sum"})
    grouped = grouped.reset_index().rename(columns={"order_date": "period", "order_id": "num_orders", "order_value": "revenue"})
    return grouped


