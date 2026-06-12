"""
Compute per-prompt average CER and processing time from any evaluation results CSV.

Reads a results CSV produced by run_evaluation.py (or the legacy per-model scripts),
flattens the 3-prompt × 3-trial structure into a long-form table, then prints and
saves prompt-level summary statistics.

Usage:
    python evaluation/calculate_averages.py results/gpt4o_results.csv
    python evaluation/calculate_averages.py results/deepseek_results.csv
"""

import argparse
import os
import sys

import pandas as pd


def summarize(input_path: str) -> pd.DataFrame:
    df = pd.read_csv(input_path)

    records = []
    for prompt in range(1, 4):
        for trial in range(1, 4):
            cer_col  = f"CER_Prompt{prompt}_Trial{trial}_vHuman"
            time_col = f"Time_Prompt{prompt}_Trial{trial}"

            if cer_col not in df.columns:
                continue

            subset = df[["NAID", cer_col, time_col]].copy()
            subset = subset.rename(columns={cer_col: "CER", time_col: "Time"})
            subset["Prompt"] = prompt
            subset["Trial"]  = trial
            records.append(subset)

    if not records:
        raise ValueError("No CER/Time columns found. Is this a valid eval results CSV?")

    df_long = pd.concat(records, ignore_index=True)

    summary = (
        df_long.groupby("Prompt")
        .agg(
            Avg_CER=("CER", "mean"),
            Std_CER=("CER", "std"),
            Avg_Time_s=("Time", "mean"),
            Std_Time_s=("Time", "std"),
        )
        .round(4)
        .reset_index()
    )
    return summary


def main():
    parser = argparse.ArgumentParser(description="Summarize eval results by prompt.")
    parser.add_argument("input_csv", help="Path to a *_results.csv file in results/.")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output CSV path. Defaults to <input_stem>_averages.csv.",
    )
    args = parser.parse_args()

    summary = summarize(args.input_csv)

    prompt_labels = {1: "Basic", 2: "Wikipedia Context", 3: "Expert"}
    print(f"\nResults for: {os.path.basename(args.input_csv)}")
    print("-" * 60)
    for _, row in summary.iterrows():
        label = prompt_labels.get(int(row["Prompt"]), f"Prompt {int(row['Prompt'])}")
        print(
            f"  {label:<20}  CER: {row['Avg_CER']:.4f} ± {row['Std_CER']:.4f}"
            f"   Time: {row['Avg_Time_s']:.1f}s ± {row['Std_Time_s']:.1f}s"
        )

    output_path = args.output
    if output_path is None:
        stem = os.path.splitext(args.input_csv)[0]
        output_path = f"{stem}_averages.csv"

    summary.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
