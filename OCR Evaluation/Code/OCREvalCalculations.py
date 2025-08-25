import pandas as pd
import os
from datetime import datetime

# --- File Paths ---
INPUT_FILE = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Results/gpt4o_eval_output.csv"
OUTPUT_DIR = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Analysis/Results"

# --- Ensure output directory exists ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Generate timestamped filename ---
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"gpt4o_eval_output_avgs_{timestamp}.csv")

# --- Load CSV ---
df = pd.read_csv(INPUT_FILE)

# --- Calculate averages for each prompt ---
for prompt in range(1, 4):  # Prompts 1, 2, 3
    # CER columns
    cer_cols = [f"CER_Prompt{prompt}_Trial{i}_vHuman" for i in range(1, 4)]
    # Time columns
    time_cols = [f"Time_Prompt{prompt}_Trial{i}" for i in range(1, 4)]
    
    # Create new average columns
    df[f"Avg_CER_Prompt{prompt}"] = df[cer_cols].mean(axis=1, skipna=True)
    df[f"Avg_Time_Prompt{prompt}"] = df[time_cols].mean(axis=1, skipna=True)

# --- Keep only NAID and new average columns ---
keep_cols = ["NAID"] + [f"Avg_CER_Prompt{p}" for p in range(1, 4)] + [f"Avg_Time_Prompt{p}" for p in range(1, 4)]
df_out = df[keep_cols]

# --- Round all numeric values to 3 decimal places ---
df_out = df_out.round(3)

# --- Save updated CSV ---
df_out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

# --- Print overall averages (excluding NAID) ---
col_means = df_out.drop(columns=["NAID"]).mean().round(3)
print("\n📊 Overall Column Averages:")
for col, val in col_means.items():
    print(f"{col}: {val}")

print(f"\n✅ Finished! New file saved at: {OUTPUT_FILE}")
