"""
Quick multi-model comparison on a subset of NAIDs using a single prompt.

Useful for spot-checking how different models perform on a handful of documents
side-by-side, without running the full 3-prompt × 3-trial evaluation suite.

Usage:
    python evaluation/run_multimodel.py
    # Edit MODELS and NAIDS_TO_PROCESS below before running.
"""

import os
import sys
import time

import pandas as pd
import requests
from openai import OpenAI

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import string_comparison

REPO_ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV    = os.path.join(REPO_ROOT, "data",    "human_transcriptions.csv")
OUTPUT_CSV   = os.path.join(REPO_ROOT, "results", "multimodel_spot_check.csv")
PROMPT_PATH  = os.path.join(REPO_ROOT, "prompts", "expert.txt")

# --- Configuration — edit these before running ---
MODELS            = ["gpt-4o-mini", "gpt-4o", "deepseek-chat"]
NAIDS_TO_PROCESS  = [28992946, 28934561, 28986666, 28974433]   # replace with desired NAIDs

# --- Load prompt ---
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    system_prompt = f.read()

# --- API Keys ---
openai_api_key   = input("OpenAI API key: ").strip()
deepseek_api_key = input("DeepSeek API key: ").strip()
openai_client    = OpenAI(api_key=openai_api_key)

# --- Load data ---
df = pd.read_csv(INPUT_CSV)
if "NAID" not in df.columns:
    raise KeyError("NAID column not found in the CSV.")

df_subset = df[df["NAID"].isin(NAIDS_TO_PROCESS)]
if df_subset.empty:
    raise ValueError("No matching NAID rows found.")

print(f"\nEvaluating {len(df_subset)} NAIDs across {len(MODELS)} models.")


def get_correction(ocr_text: str, model: str) -> str:
    if not isinstance(ocr_text, str) or len(ocr_text.strip()) < 5:
        return ""

    if model.startswith("gpt-"):
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": ocr_text},
            ],
            temperature=0.2,
            timeout=300,
        )
        return response.choices[0].message.content.strip()

    if model == "deepseek-chat":
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {deepseek_api_key}",
                "Content-Type":  "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": ocr_text},
                ],
                "temperature": 0.2,
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    return f"UNSUPPORTED_MODEL: {model}"


output_rows = []
for _, row in df_subset.iterrows():
    naid           = row.get("NAID", "UNKNOWN")
    ocr_text       = str(row.get("OCRtext", ""))
    human_text     = str(row.get("Human Text", ""))

    print(f"\nNAID: {naid}")
    result_row = {
        "NAID":              naid,
        "ocr_vs_human_CER":  string_comparison.character_error_rate(ocr_text, human_text),
    }

    for model in MODELS:
        print(f"  {model}...")
        t0         = time.time()
        correction = get_correction(ocr_text, model)
        elapsed    = round(time.time() - t0, 2)
        cer        = string_comparison.character_error_rate(correction, human_text)

        result_row[f"{model}_correction"]       = correction
        result_row[f"{model}_CER_vs_human"]     = cer
        result_row[f"{model}_response_time_s"]  = elapsed

    output_rows.append(result_row)

os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
pd.DataFrame(output_rows).to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"\nSaved to: {os.path.abspath(OUTPUT_CSV)}")
