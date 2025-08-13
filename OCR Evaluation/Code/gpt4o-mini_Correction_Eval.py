import pandas as pd
import os
import time
from openai import OpenAI
import string_comparison

# --- File Paths (update these yourself) ---
PROMPT1_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/Prompts/BasicOCRPrompt.txt"
PROMPT2_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/Prompts/WikipediaOCRPrompt.txt"
PROMPT3_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/Prompts/Expert_Prompt_ver_August 11.txt"
INPUT_CSV_PATH = "/Users/johnesposito/Downloads/HumanTranscriptions100Pages - Sheet1 (3).csv"
OUTPUT_CSV_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Results/gpt4o_mini_eval_output.csv"

# --- API Key ---
openai_api_key = input("OpenAI API Key: ").strip()
openai_client = OpenAI(api_key=openai_api_key)

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

# --- Function to call GPT-4o ---
def get_gpt4o_mini_correction(ocr_text, user_prompt):
    if not isinstance(ocr_text, str):
        ocr_text = "" if pd.isna(ocr_text) else str(ocr_text)

    messages = [{"role": "user", "content": user_prompt + ocr_text}]
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.6,
        timeout=300
    )
    return response.choices[0].message.content.strip()

# --- Main Processing ---
output_rows = []

for idx, row in df.iterrows():
    naid = row["NAID"]

    # Safe conversion for OCR text
    ocr_text = row["OCRtext"]
    if not isinstance(ocr_text, str):
        ocr_text = "" if pd.isna(ocr_text) else str(ocr_text)

    # Safe conversion for Human text
    human_text = row["Human Text"]
    if not isinstance(human_text, str):
        human_text = "" if pd.isna(human_text) else str(human_text)

    result_row = {"NAID": naid}

    for prompt_idx, prompt_text in enumerate(PROMPTS, start=1):
        for trial in range(1, 4):
            col_text = f"TEXT_Prompt{prompt_idx}_Trial{trial}"
            col_cer = f"CER_Prompt{prompt_idx}_Trial{trial}_vHuman"
            col_time = f"Time_Prompt{prompt_idx}_Trial{trial}"

            print(f"NAID {naid} | Prompt {prompt_idx} | Trial {trial}")

            start_time = time.time()
            correction = get_gpt4o_mini_correction(ocr_text, prompt_text)
            elapsed = round(time.time() - start_time, 2)

            if human_text.strip():
                cer = string_comparison.character_error_rate(correction, human_text)
            else:
                cer = None

            result_row[col_text] = correction
            result_row[col_cer] = cer
            result_row[col_time] = elapsed

    output_rows.append(result_row)

    # --- Save Every Ten Rows---
    if (idx + 1) % 10 == 0:
        results_df = pd.DataFrame(output_rows)
        results_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8")
        print(f"💾 Progress saved after {idx + 1} rows -> {OUTPUT_CSV_PATH}")



results_df = pd.DataFrame(output_rows)
results_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8")
print(f"✅ Final save to {OUTPUT_CSV_PATH}")

