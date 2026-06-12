"""
Compute Character Error Rate between raw OCR text and human-transcribed ground truth.

Reads data/human_transcriptions.csv (100 manually transcribed pages) and compares
each page's OCR text against the human-verified version to establish the baseline
CER before any LLM correction. Output is saved to results/ocr_baseline_cer.csv.

Usage:
    python evaluation/compare_ocr_vs_human.py
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import string_comparison

REPO_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV   = os.path.join(REPO_ROOT, "data",    "human_transcriptions.csv")
OUTPUT_CSV  = os.path.join(REPO_ROOT, "results", "ocr_baseline_cer.csv")

df = pd.read_csv(INPUT_CSV)

for col in ["NAID", "OCRtext", "Human Text"]:
    if col not in df.columns:
        raise KeyError(f"Required column '{col}' not found in {INPUT_CSV}.")

output_rows = []
for _, row in df.iterrows():
    ocr_text   = str(row["OCRtext"])
    human_text = str(row["Human Text"])
    cer        = string_comparison.character_error_rate(ocr_text, human_text)
    output_rows.append({
        "NAID":       row["NAID"],
        "OCR text":   ocr_text,
        "Human text": human_text,
        "CER":        cer,
    })

results_df = pd.DataFrame(output_rows)
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
results_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"Saved to: {os.path.abspath(OUTPUT_CSV)}")
