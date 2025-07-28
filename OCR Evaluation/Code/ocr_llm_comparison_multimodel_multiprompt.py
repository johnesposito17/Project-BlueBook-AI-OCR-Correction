import pandas as pd
import os
import time
import requests
import json
from openai import OpenAI
from openai.types.chat import ChatCompletion
import string_comparison

# --- Configuration ---
MODELS = ["gpt-4o-mini", "gpt-4o", "deepseek-chat"]

PROMPT_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/Prompts/JohnBlueBookPrompt5.txt"
INPUT_CSV_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Code/HumanTranscriptions100Pages - Sheet1 (1).csv"
OUTPUT_CSV_NAME = "OpenAI DeepSeek Eval Newspaper.csv"
OUTPUT_DIR = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Results"
OUTPUT_CSV_PATH = os.path.join(OUTPUT_DIR, OUTPUT_CSV_NAME)


# 🔢 List of NAIDs you want to evaluate (replace with your actual list)
NAIDS_TO_PROCESS = [28976636, 28996954, 28964100, 28932295]  # Example

# --- Load Prompt ---
def load_prompt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found at {file_path}")

system_prompt = load_prompt(PROMPT_FILE_PATH)

# --- API Keys ---
openai_api_key = input("🔑 Enter your OpenAI API key: ").strip()
deepseek_api_key = input("🔑 Enter your DeepSeek API key: ").strip()
client = OpenAI(api_key=openai_api_key)

# --- Load and Filter Input CSV ---
try:
    df = pd.read_csv(INPUT_CSV_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"Input CSV not found at: {INPUT_CSV_PATH}")

# Ensure NAID column exists
if "NAID" not in df.columns:
    raise KeyError("❌ NAID column not found in the CSV.")

# Filter rows based on specified NAIDs
df_subset = df[df["NAID"].isin(NAIDS_TO_PROCESS)]

if df_subset.empty:
    raise ValueError("❌ No matching NAID rows found in the dataset.")

print(f"\n🔍 Starting evaluation for {len(df_subset)} selected NAID rows and {len(MODELS)} models using ONE prompt.")

# --- LLM Correction Function ---
def get_llm_correction(ocr_text: str, model_name: str, system_prompt: str) -> str:
    try:
        if not isinstance(ocr_text, str) or len(ocr_text.strip()) < 5:
            return "EMPTY_OR_INVALID_INPUT"

        if model_name.startswith("gpt-"):
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ocr_text}
            ]
            response: ChatCompletion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.2,
                timeout=300
            )
            return response.choices[0].message.content.strip()

        elif model_name == "deepseek-chat":
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {deepseek_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": ocr_text}
                ],
                "temperature": 0.2
            }
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

        else:
            return f"UNSUPPORTED_MODEL: {model_name}"

    except Exception as e:
        print(f"❌ Error with model {model_name}: {e}")
        return f"API_ERROR: {e}"

# --- Main Processing Loop ---
output_rows = []

for index, row in df_subset.iterrows():
    ocr_text = row.get("OCRtext", "")
    human_transcript = row.get("Human Text", "")
    naid = row.get("NAID", "UNKNOWN")

    print(f"\n--- NAID: {naid} | Row Index: {index} ---")

    result_row = {
        "NAID": naid,
        "ocr_text": ocr_text,
        "human_transcript": human_transcript,
        "ocr_vs_human_CER": string_comparison.character_error_rate(ocr_text, human_transcript),
    }

    for model in MODELS:
        print(f"  > Evaluating Model: {model}")

        start_time = time.time()
        correction = get_llm_correction(ocr_text, model, system_prompt)
        elapsed = round(time.time() - start_time, 2)

        if "API_ERROR" in correction or "UNSUPPORTED_MODEL" in correction:
            sim_vs_human = "ERROR"
        else:
            sim_vs_human = string_comparison.character_error_rate(correction, human_transcript)

        result_row[f"{model}_correction"] = correction
        result_row[f"{model}_score_vs_human"] = sim_vs_human
        result_row[f"{model}_response_time_sec"] = elapsed

    output_rows.append(result_row)

# --- Save Output CSV ---
print("\n✅ Evaluation complete. Saving results to CSV...")
results_df = pd.DataFrame(output_rows)
results_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8")
print(f"📁 Saved to: {os.path.abspath(OUTPUT_CSV_PATH)}")
