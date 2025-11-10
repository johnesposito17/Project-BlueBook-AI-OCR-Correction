import pandas as pd
import numpy as np

# --- File Path ---
INPUT_FILE = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Results/OCR_vs_Human_CER.csv"

# --- Load Data ---
df = pd.read_csv(INPUT_FILE)

# --- Ensure CER columns are numeric ---
cer_cols = [col for col in df.columns if "CER" in col]
for col in cer_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# --- Calculate pairwise differences between CER columns ---
diffs = pd.DataFrame(index=df.index)
for i, col1 in enumerate(cer_cols):
    for j, col2 in enumerate(cer_cols):
        if j > i:  # only upper triangle (avoid duplicates)
            diffs[f"{col1}_vs_{col2}"] = (df[col1] - df[col2]).abs()

# --- Find max difference per row ---
df["Max_CER_Diff"] = diffs.max(axis=1)

# --- Threshold: flag entries with large differences ---
# you can adjust this (e.g., >0.2 or >0.3 depending on CER scale)
threshold = 0.2  
interesting = df[df["Max_CER_Diff"] > threshold]

# --- Get NAIDs for interesting cases ---
interesting_ids = interesting["NAID"].tolist()

print("Interesting NAIDs (big CER differences):")
print(interesting_ids)

# --- Save to CSV for inspection ---
interesting.to_csv("Interesting_CER_Differences.csv", index=False)
