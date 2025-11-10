"""Loads3 d ifferent correction prompts
Sends OCR text to Gemini for correction (3 trials per prompt = 9 corrections per document)
Compares corrections against human-verified text using Character Error Rate (CER)
Records the corrected text, CER scores, and processing time"""
import pandas as pd
import os
import time
import string_comparison
import google.genai as genai
from google.genai import types

# --- File Paths ---
PROMPT1_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/Prompts/BasicOCRPrompt.txt"
PROMPT2_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/Prompts/WikipediaOCRPrompt.txt"
PROMPT3_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/Prompts/Expert_Prompt_ver_August 11.txt"
INPUT_CSV_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Code/HumanTranscriptions100Pages - Sheet1 (3).csv"
OUTPUT_CSV_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Results/gemini_2.5_flash_lite_eval_output.csv"

# Ensure output folder exists
os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)

# --- API Key ---
gemini_api_key = input("Gemini API Key: ").strip()
model_name = "gemini-2.5-flash-lite"
SYSTEM_PROMPT = "You are an expert at correcting OCR text."

# --- Init Gemini Client ---
genai_client = genai.Client(api_key=gemini_api_key)

# --- Load Prompts ---
with open(PROMPT1_FILE_PATH, "r", encoding="utf-8") as f:
    prompt1 = f.read()
with open(PROMPT2_FILE_PATH, "r", encoding="utf-8") as f:
    prompt2 = f.read()
with open(PROMPT3_FILE_PATH, "r", encoding="utf-8") as f:
    prompt3 = f.read()

PROMPTS = [prompt1, prompt2, prompt3]

# --- Load Input CSV ---
df = pd.read_csv(INPUT_CSV_PATH)

if not all(col in df.columns for col in ["NAID", "OCRtext", "Human Text"]):
    raise KeyError("❌ Input CSV must contain 'NAID', 'OCRtext', and 'Human Text' columns.")

# --- Load progress if exists ---
if os.path.exists(OUTPUT_CSV_PATH):
    results_df = pd.read_csv(OUTPUT_CSV_PATH)
    completed_naids = set(results_df["NAID"])
    print(f"✅ Found existing results — {len(completed_naids)} rows completed. Resuming...")
    output_rows = results_df.to_dict("records")
else:
    completed_naids = set()
    output_rows = []
    print("ℹ️ No previous results found — starting fresh.")

# --- Gemini Request Function ---
def get_gemini_correction(ocr_text, user_prompt, retries=3):
    if not isinstance(ocr_text, str):
        ocr_text = "" if pd.isna(ocr_text) else str(ocr_text)

    for attempt in range(retries):
        try:
            response = genai_client.models.generate_content(
                model=model_name,
                contents=user_prompt + ocr_text,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.6
                ),
            )
            return response.text.strip()
        except Exception as e:
            print(f"❌ Gemini request failed on attempt {attempt+1}: {e}")
            time.sleep(2)

    return ""

# --- Main Processing ---
for idx, row in df.iterrows():
    naid = row["NAID"]

    # Skip if already processed
    if naid in completed_naids:
        continue

    ocr_text = row["OCRtext"] if isinstance(row["OCRtext"], str) else ("" if pd.isna(row["OCRtext"]) else str(row["OCRtext"]))
    human_text = row["Human Text"] if isinstance(row["Human Text"], str) else ("" if pd.isna(row["Human Text"]) else str(row["Human Text"]))

    result_row = {"NAID": naid}

    for prompt_idx, prompt_text in enumerate(PROMPTS, start=1):
        for trial in range(1, 4):
            col_text = f"TEXT_Prompt{prompt_idx}_Trial{trial}"
            col_cer = f"CER_Prompt{prompt_idx}_Trial{trial}_vHuman"
            col_time = f"Time_Prompt{prompt_idx}_Trial{trial}"

            print(f"NAID {naid} | Prompt {prompt_idx} | Trial {trial}")

            start_time = time.time()
            correction = get_gemini_correction(ocr_text, prompt_text)
            elapsed = round(time.time() - start_time, 2)

            cer = string_comparison.character_error_rate(correction, human_text) if human_text.strip() else None

            result_row[col_text] = correction
            result_row[col_cer] = cer
            result_row[col_time] = elapsed

    output_rows.append(result_row)
    completed_naids.add(naid)

    # Save every 10 rows processed
    if len(output_rows) % 10 == 0:
        pd.DataFrame(output_rows).to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8")
        print(f"💾 Progress saved at {len(output_rows)} total rows -> {OUTPUT_CSV_PATH}")

# --- Final Save ---
pd.DataFrame(output_rows).to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8")
print(f"✅ Final save to {OUTPUT_CSV_PATH}")
