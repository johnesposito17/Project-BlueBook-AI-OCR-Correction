import pandas as pd
import os
import time
import requests
import json
from openai import OpenAI
from openai.types.chat import ChatCompletion
from google import genai
from google.genai import types
import string_comparison
import sys
import getpass

# --- Configuration ---
MODELS = ["gpt-4o-mini", "gpt-4o", "deepseek-chat", "gemini-2.5-flash", "gemini-2.5-flash-lite"]



SYSTEM_PROMPT_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/Prompts/SystemPrompt.txt"
PROMPT_FILE_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/Prompts/Prompt8.txt"
INPUT_CSV_PATH = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Code/HumanTranscriptions100Pages - Sheet1 (3).csv"
OUTPUT_CSV_NAME = "Gemini_Eval_Forms1-11_Prompt7.csv"
OUTPUT_DIR = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Results"
OUTPUT_CSV_PATH = os.path.join(OUTPUT_DIR, OUTPUT_CSV_NAME)

NAIDS_TO_PROCESS = [28993832, 29000943, 28984715, 28977491, 28984139, 28994552, 28974530, 28991590]

# --- Load System Prompt ---
with open(SYSTEM_PROMPT_FILE_PATH, "r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read()

# --- Load Prompt ---
with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
    prompt = f.read()

# --- API Keys (entered by user) ---
print("🔑 Please enter your API keys (they will not be displayed):")
openai_api_key = input("OpenAI API Key: ").strip()
deepseek_api_key = input("DeepSeek API Key: ").strip()
gemini_api_key = input("Gemini API Key: ").strip()

# Initialize Clients
openai_client = OpenAI(api_key=openai_api_key)
genai_client = genai.Client(api_key=gemini_api_key)

# --- Load and Filter Input CSV ---
df = pd.read_csv(INPUT_CSV_PATH)

if "NAID" not in df.columns:
    raise KeyError("❌ NAID column not found in the CSV.")

df_subset = df[df["NAID"].isin(NAIDS_TO_PROCESS)]

print(f"\n🔍 Starting evaluation for {len(df_subset)} selected NAID rows and {len(MODELS)} models using ONE prompt.")

# --- Correction Function ---
def get_llm_correction(ocr_text, model_name):
    
    if model_name.startswith("gpt-"):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt + ocr_text}
        ]
        response: ChatCompletion = openai_client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.6,
            timeout=300
        )
        return response.choices[0].message.content.strip()

    elif model_name.startswith("deepseek-"):
        return "deepseek"
    #     url = "https://api.deepseek.com/chat/completions"
    #     headers = {
    #         "Content-Type": "application/json",
    #         "Authorization": f"Bearer {deepseek_api_key}"
    #     }
    #     payload = {
    #         "model": model_name,
    #         "messages": [
    #             {"role": "system", "content": SYSTEM_PROMPT},
    #             {"role": "user", "content": prompt + ocr_text}
    #         ],
    #         "temperature": 0.6
    #     }
    #     response = requests.post(url, headers=headers, json=payload, timeout=300)
    #     response.raise_for_status()
    #     result = response.json()
    #     return result['choices'][0]['message']['content'].strip()
    

    elif model_name.startswith("gemini-"):
        response = genai_client.models.generate_content(
            model=model_name,
            contents=prompt + ocr_text,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                system_instruction=SYSTEM_PROMPT,
                temperature=0.6
            ),
        )
        return response.text
            

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
        correction = get_llm_correction(ocr_text, model)
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
