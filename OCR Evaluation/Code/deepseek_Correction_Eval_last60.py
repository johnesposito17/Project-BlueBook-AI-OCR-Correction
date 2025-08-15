import pandas as pd
import os
import time
import requests
import string_comparison

# --- File Paths ---
PROMPT1_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/Prompts/BasicOCRPrompt.txt"
PROMPT2_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/Prompts/WikipediaOCRPrompt.txt"
PROMPT3_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/Prompts/Expert_Prompt_ver_August 11.txt"
INPUT_CSV_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Code/HumanTranscriptions100Pages - Sheet1 (3).csv"
OUTPUT_CSV_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Results/deepseek_eval_output.csv"

# Ensure output folder exists
os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)

# --- API Key ---
deepseek_api_key = input("DeepSeek API Key: ").strip()
model_name = "deepseek-chat"
url = "https://api.deepseek.com/chat/completions"

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

# --- DeepSeek Request Function with Retry ---
def get_deepseek_correction(ocr_text, user_prompt, retries=3):
    if not isinstance(ocr_text, str):
        ocr_text = "" if pd.isna(ocr_text) else str(ocr_text)

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are an expert at correcting OCR text."},
            {"role": "user", "content": user_prompt + ocr_text}
        ],
        "temperature": 0.6,
        "stream": False
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {deepseek_api_key}"
    }

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except requests.exceptions.ChunkedEncodingError:
            print(f"⚠️ ChunkedEncodingError on attempt {attempt+1}, retrying...")
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed on attempt {attempt+1}: {e}")
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
            correction = get_deepseek_correction(ocr_text, prompt_text)
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
