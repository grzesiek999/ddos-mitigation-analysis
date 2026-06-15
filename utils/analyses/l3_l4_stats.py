#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analiza logów DDoS w formacie JSONL.

Format wejścia (przykład jednej linii):
{"2026-02-22 22:57:07.468351": {"---PARAMS---": {...}, "---STATS---": {...}}}

Wymagania:
  pip install pandas matplotlib numpy

Użycie:
  1) Ustaw zmienne globalne LOG_PATHS i OUTPUT_DIR na górze pliku
  2) python analyze_ddos_jsonl.py
"""

from __future__ import annotations

import json
import os
import glob
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




LOG_PATHS = [
    str(Path(__file__).resolve().parents[2] / "logs/l3attack.jsonl"),
    str(Path(__file__).resolve().parents[2] / "logs/l4syn_attack.jsonl"),
    str(Path(__file__).resolve().parents[2] / "logs/l4udp_attack.jsonl"),
]

# Folder wyników (CSV + PNG)
OUTPUT_DIR = Path(__file__).resolve().parents[0] / "results/l3_l4_stats"


# ============================================================
# Wczytywanie i parsowanie
# ============================================================

def infer_attack_name(filepath: str) -> str:
    """Nazwa serii/ataku na podstawie nazwy pliku."""
    return Path(filepath).stem


def flatten_record(ts: str, payload: Dict[str, Any], attack: str, source_file: str) -> Dict[str, Any]:
    """Spłaszcza jedną obserwację do jednego wiersza."""
    params = payload.get("---PARAMS---", {}) or {}
    stats = payload.get("---STATS---", {}) or {}

    row: Dict[str, Any] = {
        "timestamp": ts,
        "attack": attack,
        "source_file": os.path.basename(source_file),
    }

    # PARAMS
    for k, v in params.items():
        row[f"param_{k}"] = v

    # STATS
    for k, v in stats.items():
        row[f"stat_{k}"] = v

    return row


def expand_log_paths(items: List[str]) -> List[str]:
    """Rozwija globy i filtruje do .jsonl."""
    expanded: List[str] = []
    for item in items:
        matches = glob.glob(item)
        if matches:
            expanded.extend(matches)
        else:
            expanded.append(item)

    expanded = [p for p in expanded if p.lower().endswith(".jsonl")]
    # usuń duplikaty zachowując kolejność
    seen = set()
    uniq = []
    for p in expanded:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def read_jsonl_files(filepaths: List[str]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for fp in filepaths:
        attack = infer_attack_name(fp)
        with open(fp, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"[WARN] {fp}:{line_no} JSONDecodeError: {e}")
                    continue

                if not isinstance(obj, dict) or len(obj) != 1:
                    print(f"[WARN] {fp}:{line_no} Nieoczekiwany format (spodziewany dict z 1 kluczem timestamp).")
                    continue

                ts, payload = next(iter(obj.items()))
                if not isinstance(payload, dict):
                    print(f"[WARN] {fp}:{line_no} Payload nie jest dict.")
                    continue

                rows.append(flatten_record(ts, payload, attack=attack, source_file=fp))

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # timestamp -> datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

    # Ujednolicenie liczby wątków (w Twoich logach to "Threads number")
    thread_col_candidates = [
        "param_Threads number",
        "param_Threads",
        "param_threads",
        "param_thread_count",
    ]
    df["threads"] = np.nan
    for c in thread_col_candidates:
        if c in df.columns:
            df["threads"] = df["threads"].fillna(df[c])

    # Jeśli nadal brak, ustaw 1 (często default w testach)
    df["threads"] = df["threads"].fillna(1).astype(int)

    return df


# ============================================================
# Statystyki
# ============================================================

def numeric_stat_columns(df: pd.DataFrame) -> List[str]:
    """Zwraca listę kolumn statystycznych (stat_*) liczbowych."""
    cols = [c for c in df.columns if c.startswith("stat_")]
    num_cols: List[str] = []

    for c in cols:
        if pd.api.types.is_numeric_dtype(df[c]):
            num_cols.append(c)
        else:
            converted = pd.to_numeric(df[c], errors="coerce")
            if converted.notna().any():
                df[c] = converted
                num_cols.append(c)

    return num_cols


def summarize_by_group(df: pd.DataFrame, outdir: Path) -> pd.DataFrame:
    """Statystyki per (attack, threads)."""
    outdir.mkdir(parents=True, exist_ok=True)

    num_cols = numeric_stat_columns(df)
    if not num_cols:
        print("[WARN] Brak liczbowych kolumn stat_* do analizy.")
        return pd.DataFrame()

    grp = df.groupby(["attack", "threads"], dropna=False)

    def q(x: pd.Series, p: float) -> float:
        return float(np.nanpercentile(x.to_numpy(dtype=float), p))

    agg_dict = {}
    for c in num_cols:
        agg_dict[c] = [
            "count",
            "mean",
            "std",
            "min",
            "median",
            "max",
            lambda s: q(s, 90.0),
            lambda s: q(s, 95.0),
            lambda s: q(s, 99.0),
        ]

    summary = grp.agg(agg_dict)

    summary.columns = [
        f"{col}__{fn if isinstance(fn, str) else fn.__name__}"
        for col, fn in summary.columns
    ]
    summary = summary.reset_index()

    summary_csv = outdir / "summary_by_attack_threads.csv"
    summary.to_csv(summary_csv, index=False)
    print(f"[OK] Zapisano: {summary_csv}")

    return summary


# ============================================================
# Wykresy
# ============================================================

def save_time_series_plots(df: pd.DataFrame, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    num_cols = numeric_stat_columns(df)

    preferred = [
        "stat_Pps",
        "stat_Mbps",
        "stat_Packets Sent",
        "stat_Bytes Sent",
        "stat_Errors",
    ]
    metrics = [c for c in preferred if c in df.columns] or num_cols[:5]

    for attack, dfa in df.groupby("attack"):
        dfa = dfa.sort_values("timestamp")

        for metric in metrics:
            # KLUCZOWE: pomijamy metrykę, jeśli dla tego ataku jest pusta (np. l4syn bez Mbps)
            if metric not in dfa.columns or dfa[metric].dropna().empty:
                continue

            plt.figure()
            for threads, dft in dfa.groupby("threads"):
                series = dft[metric]
                if series.dropna().empty:
                    continue
                plt.plot(dft["timestamp"], series, label=f"threads={threads}")

            plt.xlabel("czas")
            plt.ylabel(metric.replace("stat_", ""))
            plt.title(f"{attack} — {metric.replace('stat_', '')} (time series)")
            plt.legend()
            plt.tight_layout()

            fname = outdir / f"time_series__{attack}__{metric.replace('stat_', '').replace(' ', '_')}.png"
            plt.savefig(fname, dpi=160)
            plt.close()


def save_histograms(df: pd.DataFrame, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    for metric in ["stat_Pps", "stat_Mbps", "stat_Errors"]:
        if metric not in df.columns:
            continue
        if not pd.api.types.is_numeric_dtype(df[metric]):
            continue

        for attack, dfa in df.groupby("attack"):
            data = dfa[metric].dropna().to_numpy(dtype=float)
            if data.size == 0:
                continue

            plt.figure()
            plt.hist(data, bins=30)
            plt.xlabel(metric.replace("stat_", ""))
            plt.ylabel("liczność")
            plt.title(f"{attack} — histogram {metric.replace('stat_', '')}")
            plt.tight_layout()

            fname = outdir / f"hist__{attack}__{metric.replace('stat_', '').replace(' ', '_')}.png"
            plt.savefig(fname, dpi=160)
            plt.close()


def save_boxplots_by_threads(df: pd.DataFrame, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    metric = "stat_Pps" if "stat_Pps" in df.columns else None
    if metric is None or not pd.api.types.is_numeric_dtype(df[metric]):
        return

    for attack, dfa in df.groupby("attack"):
        groups = []
        labels = []

        for threads, dft in sorted(dfa.groupby("threads"), key=lambda x: x[0]):
            vals = dft[metric].dropna().to_numpy(dtype=float)
            if vals.size == 0:
                continue
            groups.append(vals)
            labels.append(str(threads))

        if len(groups) < 2:
            continue

        plt.figure()
        plt.boxplot(groups, labels=labels, showmeans=True)
        plt.xlabel("threads")
        plt.ylabel(metric.replace("stat_", ""))
        plt.title(f"{attack} — {metric.replace('stat_', '')} (boxplot vs threads)")
        plt.tight_layout()

        fname = outdir / f"boxplot__{attack}__{metric.replace('stat_', '').replace(' ', '_')}.png"
        plt.savefig(fname, dpi=160)
        plt.close()


def save_correlation_heatmap(df: pd.DataFrame, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    num_cols = numeric_stat_columns(df)
    if len(num_cols) < 2:
        return

    for attack, dfa in df.groupby("attack"):
        dfn = dfa[num_cols].copy().dropna(axis=1, how="all")
        if dfn.shape[1] < 2:
            continue

        corr = dfn.corr(numeric_only=True)

        plt.figure()
        plt.imshow(corr.to_numpy(), aspect="auto")
        plt.xticks(
            range(len(corr.columns)),
            [c.replace("stat_", "") for c in corr.columns],
            rotation=45,
            ha="right",
        )
        plt.yticks(range(len(corr.index)), [c.replace("stat_", "") for c in corr.index])
        plt.title(f"{attack} — korelacje (Pearson)")
        plt.colorbar()
        plt.tight_layout()

        fname = outdir / f"corr__{attack}.png"
        plt.savefig(fname, dpi=160)
        plt.close()


# ============================================================
# RUN
# ============================================================

def run_analysis() -> None:
    filepaths = expand_log_paths(LOG_PATHS)
    if not filepaths:
        raise SystemExit("Nie znaleziono plików .jsonl w LOG_PATHS (sprawdź ścieżki/globy).")

    outdir = Path(OUTPUT_DIR)
    outdir.mkdir(parents=True, exist_ok=True)

    df = read_jsonl_files(filepaths)
    if df.empty:
        raise SystemExit("Wczytano 0 rekordów. Sprawdź format plików.")

    flat_csv = outdir / "flattened_all_records.csv"
    df.to_csv(flat_csv, index=False)
    print(f"[OK] Zapisano: {flat_csv}")

    _summary = summarize_by_group(df, outdir=outdir)

    plots_dir = outdir / "plots"
    save_time_series_plots(df, plots_dir)
    save_histograms(df, plots_dir)
    save_boxplots_by_threads(df, plots_dir)
    save_correlation_heatmap(df, plots_dir)

    print(f"[OK] Wykresy zapisane w: {plots_dir.resolve()}")