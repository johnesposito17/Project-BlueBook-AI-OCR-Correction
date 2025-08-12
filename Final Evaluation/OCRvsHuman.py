import string_comparison
import pandas as pd
import os

# --- Configuration ---
INPUT_CSV_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Code/HumanTranscriptions100Pages - Sheet1 (2).csv"
OUTPUT_CSV_NAME = "OCR_vs_Human_CER.csv"
OUTPUT_DIR = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Results"
OUTPUT_CSV_PATH = os.path.join(OUTPUT_DIR, OUTPUT_CSV_NAME)

# --- Load Input CSV ---
df = pd.read_csv(INPUT_CSV_PATH)

# Check necessary columns
required_cols = ["NAID", "OCRtext", "Human Text"]
for col in required_cols:
    if col not in df.columns:
        raise KeyError(f"❌ Required column '{col}' not found in the CSV.")

# --- Compute CER for each row ---
output_rows = []
for index, row in df.iterrows():
    naid = row["NAID"]
    ocr_text = str(row["OCRtext"])
    human_text = str(row["Human Text"])
    
    cer = string_comparison.character_error_rate(ocr_text, human_text)
    
    output_rows.append({
        "NAID": naid,
        "OCR text": ocr_text,
        "Human text": human_text,
        "CER": cer
    })

# --- Save Results ---
results_df = pd.DataFrame(output_rows)
results_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8")

print(f"✅ CER calculation complete. Saved to: {os.path.abspath(OUTPUT_CSV_PATH)}")
