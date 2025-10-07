from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_rfm_histograms(rfm: pd.DataFrame, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    axes = axes.ravel()
    rfm["recency_days"].plot(kind="hist", bins=30, ax=axes[0], color="#1f77b4"); axes[0].set_title("Recency (days)")
    rfm["frequency"].plot(kind="hist", bins=30, ax=axes[1], color="#ff7f0e"); axes[1].set_title("Frequency (orders)")
    rfm["monetary"].plot(kind="hist", bins=30, ax=axes[2], color="#2ca02c"); axes[2].set_title("Monetary (revenue)")
    for ax in axes:
        ax.grid(True, linestyle=":", alpha=0.4)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_cohort_retention_heatmap(matrix: pd.DataFrame, output_path: str | Path, vmax: Optional[float] = 1.0) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    data = matrix.copy()
    im = ax.imshow(data.values, aspect="auto", cmap="Blues", vmin=0.0, vmax=vmax)
    ax.set_yticks(range(len(data.index)))
    ax.set_yticklabels([d.strftime("%Y-%m") for d in data.index])
    ax.set_xticks(range(len(data.columns)))
    ax.set_xticklabels([str(int(c)) for c in data.columns])
    ax.set_xlabel("Months Since Cohort")
    ax.set_ylabel("Cohort (Year-Month)")
    ax.set_title("Cohort Retention")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Retention")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_orders_over_time(agg: pd.DataFrame, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax2 = ax1.twinx()

    ax1.plot(agg["period"], agg["num_orders"], color="#1f77b4", label="Orders")
    ax2.plot(agg["period"], agg["revenue"], color="#ff7f0e", label="Revenue")

    ax1.set_xlabel("Period")
    ax1.set_ylabel("Orders", color="#1f77b4")
    ax2.set_ylabel("Revenue", color="#ff7f0e")
    ax1.grid(True, linestyle=":", alpha=0.4)
    fig.suptitle("Orders and Revenue Over Time")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


