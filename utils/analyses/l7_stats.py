# -*- coding: utf-8 -*-

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path




LOGS_DIR = str(Path(__file__).resolve().parents[2] / "logs/l7attack.jsonl")
OUTPUT_DIR = str(Path(__file__).resolve().parents[0] / "results/l7_stats")

# =========================


def load_jsonl_file(filepath):
    records = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            obj = json.loads(line)
            date_key = next(iter(obj.keys()))
            payload = obj[date_key]

            params = payload.get("---PARAMS---", {})
            stats = payload.get("---STATS---", {})

            rec = {
                "timestamp": date_key.replace("DATE:", "").strip()
            }

            rec.update(params)
            rec.update(stats)

            records.append(rec)

    df = pd.DataFrame(records)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    if "Requests" in df.columns and "Errors" in df.columns:
        df["error_rate"] = np.where(
            df["Requests"] > 0,
            df["Errors"] / df["Requests"],
            np.nan
        )

    return df


def filter_proxy(df, proxy_mode):
    if proxy_mode == "all":
        return df

    if "Proxy" not in df.columns:
        print("Brak kolumny Proxy — filtr pominięty")
        return df

    return df[df["Proxy"] == proxy_mode].copy()


def compute_group_stats(df):

    metrics = [
        col for col in df.columns
        if col not in ["timestamp", "Bot Count", "Rps", "Proxy"]
        and pd.api.types.is_numeric_dtype(df[col])
    ]

    grouped = df.groupby(["Bot Count", "Rps", "Proxy"]).agg(
        {m: ["mean", "std", "min", "max", "count"] for m in metrics}
    )

    grouped.columns = [
        f"{col}_{stat}" for col, stat in grouped.columns.to_flat_index()
    ]

    grouped = grouped.reset_index()

    return grouped, metrics


def plot_metric_lines(grouped, metric, proxy_mode):
    mean_col = f"{metric}_mean"
    std_col = f"{metric}_std"

    plt.figure()

    for bot_count, sub in grouped.groupby("Bot Count"):
        sub = sub.sort_values("Rps")

        x = sub["Rps"]
        y = sub[mean_col]

        plt.plot(x, y, label=f"{bot_count} bots")

        if std_col in sub.columns:
            s = sub[std_col]
            plt.fill_between(x, y - s, y + s, alpha=0.15)

    plt.title(f"{metric} vs Rps | Proxy={proxy_mode}")
    plt.xlabel("Rps")
    plt.ylabel(metric)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    filename = os.path.join(
        OUTPUT_DIR,
        f"{metric}_lines_proxy_{proxy_mode}.png"
    )
    plt.savefig(filename, dpi=200)
    plt.close()


def plot_heatmap(grouped, metric, proxy_mode):
    mean_col = f"{metric}_mean"

    pivot = grouped.pivot_table(
        index="Bot Count",
        columns="Rps",
        values=mean_col
    )

    plt.figure()
    plt.imshow(pivot, aspect="auto")
    plt.colorbar()

    plt.title(f"Heatmap {metric} | Proxy={proxy_mode}")
    plt.xlabel("Rps")
    plt.ylabel("Bot Count")

    plt.xticks(
        range(len(pivot.columns)),
        pivot.columns,
        rotation=45
    )
    plt.yticks(
        range(len(pivot.index)),
        pivot.index
    )

    plt.tight_layout()

    filename = os.path.join(
        OUTPUT_DIR,
        f"{metric}_heatmap_proxy_{proxy_mode}.png"
    )
    plt.savefig(filename, dpi=200)
    plt.close()


def save_csv(df, name):
    path = os.path.join(OUTPUT_DIR, name)
    df.to_csv(path, index=False)


# =========================
# ========= MAIN ==========
# =========================

def run_l7_stats(proxy: bool):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = load_jsonl_file(LOGS_DIR)

    df = filter_proxy(df, proxy)

    grouped, metrics = compute_group_stats(df)

    save_csv(df, f"raw_proxy_{proxy}.csv")
    save_csv(grouped, f"grouped_stats_proxy_{proxy}.csv")

    # Wykresy dla kluczowych metryk
    for metric in ["Requests", "error_rate", "p95", "p99"]:
        if metric in metrics:
            plot_metric_lines(grouped, metric, proxy)
            plot_heatmap(grouped, metric, proxy)

    print("Analiza zakończona.")
    print("Wyniki zapisane w:", OUTPUT_DIR)
