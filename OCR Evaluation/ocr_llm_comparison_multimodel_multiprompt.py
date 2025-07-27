import pandas as pd
import os
import time
import requests
import json
from openai import OpenAI
from openai.types.chat import ChatCompletion
import string_comparison

# --- Configuration ---
MODELS = ["gpt-4o-mini", "gpt-4o", "tinyLlama", "llama3"]
OLLAMA_URL = "http://localhost:11434/api/chat"

# Prompt file paths
WIKI_PROMPT_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/WikipediaOCRPrompt.txt"
GENERIC_PROMPT_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/GenericOCRPrompt.txt"

# Input and output paths
INPUT_CSV_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/FilesForHumanTranscription - Sheet1.csv"
OUTPUT_CSV_NAME = "OCR Eval 4 models output.csv"
OUTPUT_CSV_PATH = os.path.join(os.path.dirname(INPUT_CSV_PATH), OUTPUT_CSV_NAME)

ROWS_TO_PROCESS = 5

# --- Load Prompts ---
def load_prompt(file_path, fallback_text):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"⚠️ Warning: Prompt file not found at {file_path}. Using fallback.")
        return fallback_text

PROMPTS = {
    "wikipedia_prompt": load_prompt(WIKI_PROMPT_FILE_PATH, "Correct the following OCR text using contextual Wikipedia knowledge."),
    "generic_prompt": load_prompt(GENERIC_PROMPT_FILE_PATH, "Correct the following OCR text."),
}

# --- Setup OpenAI Client ---
api_key = input("Enter your OpenAI API key: ").strip()
client = OpenAI(api_key=api_key)

# --- Load Input CSV ---
try:
    df = pd.read_csv(INPUT_CSV_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"Input CSV not found at: {INPUT_CSV_PATH}")

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
                temperature=0.3,
                timeout=300
            )
            return response.choices[0].message.content.strip()

        elif model_name in ["tinyLlama", "llama3"]:
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": ocr_text}
                ],
                "temperature": 0.3,
                "stream": False
            }
            response = requests.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            parsed = response.json()
            return parsed["message"]["content"].strip()

        else:
            return f"UNSUPPORTED_MODEL: {model_name}"

    except Exception as e:
        print(f"❌ Error with model {model_name}: {e}")
        return f"API_ERROR: {e}"

# --- Main Processing Loop ---
df_subset = df.head(ROWS_TO_PROCESS)
output_rows = []

print(f"🔍 Starting evaluation for {len(df_subset)} rows, {len(MODELS)} models, and {len(PROMPTS)} prompts.")

for index, row in df_subset.iterrows():
    ocr_text = row.get("OCRtext", "")
    human_transcript = row.get("Human Text", "")

    print(f"\n--- Row {index + 1} ---")

    result_row = {
        "ocr_text": ocr_text,
        "human_transcript": human_transcript,
    }

    # Compute OCR vs Human CER once per row
    sim_ocr_vs_human = string_comparison.character_error_rate(ocr_text, human_transcript)
    result_row["ocr_vs_human_CER"] = sim_ocr_vs_human

    for model in MODELS:
        for prompt_key, prompt_text in PROMPTS.items():
            label_prefix = f"{model}_{prompt_key}"
            print(f"  > Model: {model}, Prompt: {prompt_key}")

            start_time = time.time()
            correction = get_llm_correction(ocr_text, model, prompt_text)
            elapsed = round(time.time() - start_time, 2)

            if "API_ERROR" in correction or "UNSUPPORTED_MODEL" in correction:
                print(f"⚠️ Skipping similarity for model {model} due to error.")
                sim_vs_human = "ERROR"
            else:
                sim_vs_human = string_comparison.character_error_rate(correction, human_transcript)

            result_row[f"{label_prefix}_correction"] = correction
            result_row[f"{label_prefix}_score_vs_human"] = sim_vs_human
            result_row[f"{label_prefix}_response_time_sec"] = elapsed

    output_rows.append(result_row)

# --- Save Output CSV ---
print("\n✅ Evaluation complete. Saving results to CSV...")
results_df = pd.DataFrame(output_rows)
results_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8")
print(f"📁 Saved to: {os.path.abspath(OUTPUT_CSV_PATH)}")
