import pandas as pd
import os
import time
import requests
import json
from openai import OpenAI
from openai.types.chat import ChatCompletion
import string_comparison
import sys

# --- Configuration ---
MODELS = ["gpt-4o-mini", "gpt-4o", "gemini-2.5-pro", "gemini-2.5-flash"]

PROMPT_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/Prompts/GenericOCRPrompt.txt"
INPUT_CSV_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Code/HumanTranscriptions100Pages - Sheet1 (1).csv"
OUTPUT_CSV_NAME = "OpenAI_DeepSeek_Gemini_Eval_Prompt6_v3.csv"
OUTPUT_DIR = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Results"
OUTPUT_CSV_PATH = os.path.join(OUTPUT_DIR, OUTPUT_CSV_NAME)

# 🔢 NAIDs to evaluate
NAIDS_TO_PROCESS = [28976636, 28996954, 28964100, 28932295]

# --- Load Prompt ---
def load_prompt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found at {file_path}")

system_prompt = load_prompt(PROMPT_FILE_PATH)

# --- API Keys (loaded from environment variables) ---
openai_api_key = "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"
deepseek_api_key = "sk-5eb5793dbaf04f249b5e59cd3835355b"
gemini_api_key = "AIzaSyDySIIG-x5sYyD-PGaRAqsOh2lU-2jPyjM"

if not all([openai_api_key, deepseek_api_key, gemini_api_key]):
    raise ValueError("❌ One or more API keys are missing. Please set them as environment variables.")

client = OpenAI(api_key=openai_api_key)

# --- Load and Filter Input CSV ---
try:
    df = pd.read_csv(INPUT_CSV_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"Input CSV not found at: {INPUT_CSV_PATH}")

if "NAID" not in df.columns:
    raise KeyError("❌ NAID column not found in the CSV.")

df_subset = df[df["NAID"].isin(NAIDS_TO_PROCESS)]

if df_subset.empty:
    raise ValueError("❌ No matching NAID rows found in the dataset.")

print(f"\n🔍 Starting evaluation for {len(df_subset)} selected NAID rows and {len(MODELS)} models using ONE prompt.")

# --- Correction Function ---
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

        elif model_name.startswith("deepseek-"):
            url = "https://api.deepseek.com/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {deepseek_api_key}"
            }
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": ocr_text}
                ],
                "temperature": 0.2
            }
            response = requests.post(url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()

        elif model_name.startswith("gemini-"):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
            headers = {"Content-Type": "application/json"}
            params = {"key": gemini_api_key}
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": ocr_text}]}
                ],
                "system_instruction": {
                    "parts": [{"text": system_prompt}]
                },
                "generationConfig": {
                    "temperature": 0.2
                }
            }
            response = requests.post(url, headers=headers, params=params, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            if "candidates" in result and result["candidates"] and "content" in result["candidates"][0] and "parts" in result["candidates"][0]["content"] and result["candidates"][0]["content"]["parts"]:
                 return result["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                 return f"EMPTY_RESPONSE_FROM_API: {result.get('promptFeedback', 'No feedback provided')}"

        else:
            return f"UNSUPPORTED_MODEL: {model_name}"

    except requests.exceptions.Timeout:
        print(f"❌ Timeout error with model {model_name}.")
        return "API_ERROR: Request timed out."
    except requests.exceptions.RequestException as e:
        # Catch connection errors specifically and give a targeted message
        error_details = str(e)
        if "NameResolutionError" in error_details:
             print(f"❌ DNS/Network error for {model_name}: Could not resolve hostname. Check your internet connection and firewall.")
             return f"API_ERROR: DNS/Network issue - {e}"
        if hasattr(e, 'response') and e.response is not None:
             error_details = f"{e}. Response: {e.response.text[:200]}"
        print(f"❌ Error with model {model_name}: {error_details}")
        return f"API_ERROR: {error_details}"
    except Exception as e:
        print(f"❌ An unexpected error occurred with model {model_name}: {e}")
        return f"API_ERROR: {e}"

# --- Main Loop ---
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

        if any(err_tag in correction for err_tag in ["API_ERROR", "UNSUPPORTED_MODEL", "EMPTY_RESPONSE_FROM_API"]):
            sim_vs_human = "ERROR"
        else:
            sim_vs_human = string_comparison.character_error_rate(correction, human_transcript)

        result_row[f"{model}_correction"] = correction
        result_row[f"{model}_score_vs_human"] = sim_vs_human
        result_row[f"{model}_response_time_sec"] = elapsed

    output_rows.append(result_row)

# --- Save Results ---
print("\n✅ Evaluation complete. Saving results to CSV...")
results_df = pd.DataFrame(output_rows)
results_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8")
print(f"📁 Saved to: {os.path.abspath(OUTPUT_CSV_PATH)}")