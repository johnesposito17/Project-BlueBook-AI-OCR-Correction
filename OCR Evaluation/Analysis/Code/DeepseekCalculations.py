import pandas as pd
import os
from datetime import datetime

# --- File Paths ---
INPUT_FILE = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Results/deepseek_eval_output.csv"
OUTPUT_DIR = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Analysis/Results"

# --- Ensure output directory exists ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Generate timestamped filename ---
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"deepseek_eval_output_avgs_{timestamp}.csv")

# --- Load CSV ---
df = pd.read_csv(INPUT_FILE)

# --- Reshape into long format (NAID × Prompt × Trial) ---
records = []
for prompt in range(1, 4):
    for trial in range(1, 4):
        cer_col = f"CER_Prompt{prompt}_Trial{trial}_vHuman"
        time_col = f"Time_Prompt{prompt}_Trial{trial}"
        
        subset = df[["NAID", cer_col, time_col]].copy()
        subset = subset.rename(columns={
            cer_col: "CER",
            time_col: "Time"
        })
        subset["Prompt"] = prompt
        subset["Trial"] = trial
        records.append(subset)

df_long = pd.concat(records, ignore_index=True)

# --- Compute statistics directly at trial level ---
summary = df_long.groupby("Prompt").agg(
    Avg_CER=("CER", "mean"),
    Std_CER=("CER", "std"),
    Avg_Time=("Time", "mean"),
    Std_Time=("Time", "std")
).reset_index()

# --- Round values ---
summary = summary.round(3)

# --- Save summary CSV ---
summary.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

# --- Print results in requested format ---
print("\n📊 Overall Column Statistics (trial-level across all NAIDs):")
for _, row in summary.iterrows():
    print(f"Prompt {int(row['Prompt'])}: "
          f"CER mean = {row['Avg_CER']}, std = {row['Std_CER']} | "
          f"Time mean = {row['Avg_Time']}, std = {row['Std_Time']}")

print(f"\n✅ Finished! New file saved at: {OUTPUT_FILE}")
