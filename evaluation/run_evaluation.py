"""
Run OCR correction evaluation for a single model against all three prompts.

Sends each document's OCR text to the chosen model three times per prompt
(3 prompts × 3 trials = 9 corrections per document), computes Character Error
Rate (CER) against human-transcribed ground truth, and saves results to
results/<model>_results.csv.

Usage:
    python evaluation/run_evaluation.py --model gpt-4o
    python evaluation/run_evaluation.py --model gpt-4o-mini
    python evaluation/run_evaluation.py --model gpt-5
    python evaluation/run_evaluation.py --model gemini-2.5-flash
    python evaluation/run_evaluation.py --model gemini-2.5-flash-lite
    python evaluation/run_evaluation.py --model deepseek-chat
"""

import argparse
import os
import sys
import time

import pandas as pd

# Make evaluation/ importable as a package regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import string_comparison

# ---------------------------------------------------------------------------
# Paths (relative to repo root — run from there)
# ---------------------------------------------------------------------------
REPO_ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV      = os.path.join(REPO_ROOT, "data", "human_transcriptions.csv")
PROMPT_PATHS   = [
    os.path.join(REPO_ROOT, "prompts", "basic.txt"),
    os.path.join(REPO_ROOT, "prompts", "wikipedia_context.txt"),
    os.path.join(REPO_ROOT, "prompts", "expert.txt"),
]
RESULTS_DIR    = os.path.join(REPO_ROOT, "results")

OPENAI_MODELS  = {"gpt-4o", "gpt-4o-mini", "gpt-5"}
GEMINI_MODELS  = {"gemini-2.5-flash", "gemini-2.5-flash-lite"}
DEEPSEEK_MODEL = "deepseek-chat"


def load_prompts():
    prompts = []
    for path in PROMPT_PATHS:
        with open(path, "r", encoding="utf-8") as f:
            prompts.append(f.read())
    return prompts


def safe_str(val) -> str:
    if isinstance(val, str):
        return val
    return "" if pd.isna(val) else str(val)


# ---------------------------------------------------------------------------
# Model-specific call functions
# ---------------------------------------------------------------------------

def call_openai(client, model: str, prompt: str, ocr_text: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt + ocr_text}],
        temperature=0.6,
        timeout=300,
    )
    return response.choices[0].message.content.strip()


def call_gemini(client, model: str, prompt: str, ocr_text: str, retries: int = 3) -> str:
    from google.genai import types

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt + ocr_text,
                config=types.GenerateContentConfig(
                    system_instruction="You are an expert at correcting OCR text.",
                    temperature=0.6,
                ),
            )
            return response.text.strip()
        except Exception as e:
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"  Gemini error (attempt {attempt + 1}): {e} — retrying in {wait}s")
                time.sleep(wait)
            else:
                raise


def call_deepseek(api_key: str, prompt: str, ocr_text: str) -> str:
    import requests as req

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are an expert at correcting OCR text."},
            {"role": "user", "content": prompt + ocr_text},
        ],
        "temperature": 0.6,
    }
    response = req.post(
        "https://api.deepseek.com/chat/completions",
        headers=headers,
        json=payload,
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Evaluate OCR correction for one model.")
    parser.add_argument(
        "--model",
        required=True,
        choices=sorted(OPENAI_MODELS | GEMINI_MODELS | {DEEPSEEK_MODEL}),
        help="Model to evaluate.",
    )
    args = parser.parse_args()
    model = args.model

    # --- Load data ---
    df = pd.read_csv(INPUT_CSV)
    if not all(c in df.columns for c in ["NAID", "OCRtext", "Human Text"]):
        raise KeyError("Input CSV must contain 'NAID', 'OCRtext', and 'Human Text'.")

    prompts = load_prompts()

    # --- Determine output path and any already-completed rows ---
    safe_name = model.replace("/", "_").replace(".", "_")
    output_path = os.path.join(RESULTS_DIR, f"{safe_name}_results.csv")
    os.makedirs(RESULTS_DIR, exist_ok=True)

    if os.path.exists(output_path):
        existing = pd.read_csv(output_path)
        done_naids = set(existing["NAID"])
        output_rows = existing.to_dict("records")
        print(f"Resuming — {len(done_naids)} rows already complete.")
    else:
        done_naids = set()
        output_rows = []

    # --- Set up client ---
    client = None
    deepseek_key = None

    if model in OPENAI_MODELS:
        from openai import OpenAI
        api_key = input("OpenAI API key: ").strip()
        client = OpenAI(api_key=api_key)
    elif model in GEMINI_MODELS:
        import google.genai as genai
        api_key = input("Google Gemini API key: ").strip()
        client = genai.Client(api_key=api_key)
    else:
        deepseek_key = input("DeepSeek API key: ").strip()

    # --- Process rows ---
    for _, row in df.iterrows():
        naid = row["NAID"]
        if naid in done_naids:
            continue

        ocr_text   = safe_str(row["OCRtext"])
        human_text = safe_str(row["Human Text"])
        result_row = {"NAID": naid}

        for p_idx, prompt_text in enumerate(prompts, start=1):
            for trial in range(1, 4):
                col_text = f"TEXT_Prompt{p_idx}_Trial{trial}"
                col_cer  = f"CER_Prompt{p_idx}_Trial{trial}_vHuman"
                col_time = f"Time_Prompt{p_idx}_Trial{trial}"

                print(f"  NAID {naid} | Prompt {p_idx} | Trial {trial}")
                t0 = time.time()

                try:
                    if model in OPENAI_MODELS:
                        correction = call_openai(client, model, prompt_text, ocr_text)
                    elif model in GEMINI_MODELS:
                        correction = call_gemini(client, model, prompt_text, ocr_text)
                    else:
                        correction = call_deepseek(deepseek_key, prompt_text, ocr_text)
                except Exception as e:
                    print(f"    ERROR: {e}")
                    correction = ""

                elapsed = round(time.time() - t0, 2)
                cer = string_comparison.character_error_rate(correction, human_text) if human_text.strip() else None

                result_row[col_text] = correction
                result_row[col_cer]  = cer
                result_row[col_time] = elapsed

        output_rows.append(result_row)
        # Save after every row so progress survives interruptions
        pd.DataFrame(output_rows).to_csv(output_path, index=False, encoding="utf-8")

    print(f"\nDone. Results saved to: {output_path}")


if __name__ == "__main__":
    main()
