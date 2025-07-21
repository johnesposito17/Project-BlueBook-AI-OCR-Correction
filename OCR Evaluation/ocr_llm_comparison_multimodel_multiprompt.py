# import pandas as pd
# import os
# import time
# from openai import OpenAI
# from openai.types.chat import ChatCompletion
# import string_comparison



# # --- Configuration ---

# MODELS = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]

# PROMPT_FILE_PATH = "/Users/johnesposito/Documents/Summer 2025 Code/OAI API Integration/BlueBook_complex_prompt.txt"
# try:
#     with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
#         complex_prompt = f.read()
# except FileNotFoundError:
#     print(f"Warning: Prompt file not found at {PROMPT_FILE_PATH}. Using a default prompt.")
#     complex_prompt = "Please correct the following OCR text. Be precise and only return the corrected text."

# PROMPTS = {
#     "complex_prompt": complex_prompt,
#     "simple_prompt": "Correct the following OCR text:",
# }

# INPUT_CSV_PATH = "/Users/johnesposito/Downloads/FilesForHumanTranscriptionPartialJul17 - Sheet1 (2).csv"
# OUTPUT_CSV_PATH = "ocr_llm_comparison_wideformat_results.csv"
# ROWS_TO_PROCESS = 3

# # --- Setup ---

# api_key = input("Enter your OpenAI API key: ").strip()
# client = OpenAI(api_key=api_key)

# try:
#     df = pd.read_csv(INPUT_CSV_PATH)
# except FileNotFoundError:
#     raise FileNotFoundError(f"Input CSV not found at: {INPUT_CSV_PATH}")

# # --- Functions ---

# def get_llm_correction(ocr_text: str, model_name: str, system_prompt: str) -> str:
#     try:
#         if not isinstance(ocr_text, str) or len(ocr_text.strip()) < 5:
#             return "EMPTY_OR_INVALID_INPUT"

#         messages = [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": ocr_text}
#         ]

#         response: ChatCompletion = client.chat.completions.create(
#             model=model_name,
#             messages=messages,
#             temperature=0.3,
#             timeout=300
#         )

#         return response.choices[0].message.content.strip()

#     except Exception as e:
#         print(f"Error calling OpenAI API for model {model_name}: {e}")
#         return f"API_ERROR: {e}"



# # def calculate_similarity(string1: str, string2: str) -> int:
# #     if not isinstance(string1, str) or not isinstance(string2, str):
# #         return 0
# #     return string_comparison.character_error_rate(string1, string2)

# # --- Main Processing Loop ---

# df_subset = df.head(ROWS_TO_PROCESS)
# output_rows = []

# print(f"Starting wide-format evaluation for {len(df_subset)} rows, {len(MODELS)} models, and {len(PROMPTS)} prompts.")

# for index, row in df_subset.iterrows():
#     ocr_text = row.get("OCRtext", "")
#     human_transcript = row.get("Human Text", "")
    
#     print(f"\n--- Row {index} ---")
    
#     result_row = {
#         "ocr_text": ocr_text,
#         "human_transcript": human_transcript,
#     }

#     for model in MODELS:
#         for prompt_key, prompt_text in PROMPTS.items():
#             label_prefix = f"{model}_{prompt_key}"
#             print(f"  > Model: {model}, Prompt: {prompt_key}")

#             start_time = time.time()
#             correction = get_llm_correction(ocr_text, model, prompt_text)
#             elapsed = round(time.time() - start_time, 2)

#             sim_vs_ocr = string_comparison.character_error_rate(correction, ocr_text)
#             sim_vs_human = string_comparison.character_error_rate(correction, human_transcript)

#             result_row[f"{label_prefix}_correction"] = correction
#             result_row[f"{label_prefix}_score_vs_ocr"] = sim_vs_ocr
#             result_row[f"{label_prefix}_score_vs_human"] = sim_vs_human
#             result_row[f"{label_prefix}_response_time_sec"] = elapsed

#     output_rows.append(result_row)

# # --- Save to CSV ---

# print("\n✅ Evaluation complete. Saving wide-format results to CSV...")

# results_df = pd.DataFrame(output_rows)
# results_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8")

# print(f"Saved to: {os.path.abspath(OUTPUT_CSV_PATH)}")


import pandas as pd
import os
import time
import requests
import json
from openai import OpenAI
from openai.types.chat import ChatCompletion
import string_comparison

# --- Configuration ---
MODELS = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo", "tinyllama"]

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"

PROMPT_FILE_PATH = "/Users/johnesposito/Documents/Summer 2025 Code/OAI API Integration/BlueBook_complex_prompt.txt"
try:
    with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
        complex_prompt = f.read()
except FileNotFoundError:
    print(f"Warning: Prompt file not found at {PROMPT_FILE_PATH}. Using a default prompt.")
    complex_prompt = "Please correct the following OCR text. Be precise and only return the corrected text."

PROMPTS = {
    "complex_prompt": complex_prompt,
    "simple_prompt": "Correct the following OCR text:",
}

INPUT_CSV_PATH = "/Users/johnesposito/Downloads/FilesForHumanTranscriptionPartialJul17 - Sheet1 (2).csv"
OUTPUT_CSV_PATH = "ocr_llm_comparison_wideformat_results.csv"
ROWS_TO_PROCESS = 3

# --- Setup ---
api_key = input("Enter your OpenAI API key: ").strip()
client = OpenAI(api_key=api_key)

try:
    df = pd.read_csv(INPUT_CSV_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"Input CSV not found at: {INPUT_CSV_PATH}")

# --- Functions ---
def get_llm_correction(ocr_text: str, model_name: str, system_prompt: str) -> str:
    try:
        if not isinstance(ocr_text, str) or len(ocr_text.strip()) < 5:
            return "EMPTY_OR_INVALID_INPUT"

        # OpenAI model
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

        # Ollama model (e.g. tinyllama)
        elif model_name == "tinyllama":
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
        print(f"Error with model {model_name}: {e}")
        return f"API_ERROR: {e}"

# --- Main Processing Loop ---
df_subset = df.head(ROWS_TO_PROCESS)
output_rows = []

print(f"Starting wide-format evaluation for {len(df_subset)} rows, {len(MODELS)} models, and {len(PROMPTS)} prompts.")

for index, row in df_subset.iterrows():
    ocr_text = row.get("OCRtext", "")
    human_transcript = row.get("Human Text", "")
    
    print(f"\n--- Row {index} ---")
    
    result_row = {
        "ocr_text": ocr_text,
        "human_transcript": human_transcript,
    }

    for model in MODELS:
        for prompt_key, prompt_text in PROMPTS.items():
            label_prefix = f"{model}_{prompt_key}"
            print(f"  > Model: {model}, Prompt: {prompt_key}")

            start_time = time.time()
            correction = get_llm_correction(ocr_text, model, prompt_text)
            elapsed = round(time.time() - start_time, 2)

            if "API_ERROR" in correction or "UNSUPPORTED_MODEL" in correction:
                print(f"⚠️ Skipping similarity for model {model} due to error.")
                sim_vs_ocr = "ERROR"
                sim_vs_human = "ERROR"
            else:
                sim_vs_ocr = string_comparison.character_error_rate(correction, ocr_text)
                sim_vs_human = string_comparison.character_error_rate(correction, human_transcript)

            result_row[f"{label_prefix}_correction"] = correction
            result_row[f"{label_prefix}_score_vs_ocr"] = sim_vs_ocr
            result_row[f"{label_prefix}_score_vs_human"] = sim_vs_human
            result_row[f"{label_prefix}_response_time_sec"] = elapsed

    output_rows.append(result_row)

# --- Save to CSV ---
print("\n✅ Evaluation complete. Saving wide-format results to CSV...")
results_df = pd.DataFrame(output_rows)
results_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8")
print(f"Saved to: {os.path.abspath(OUTPUT_CSV_PATH)}")
