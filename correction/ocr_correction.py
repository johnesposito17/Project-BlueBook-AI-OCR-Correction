"""
Apply LLM-based OCR correction to the full Project Blue Book dataset.

Loads the raw OCR CSV downloaded via data/download_from_archives.py, sends each
document's OCR text to GPT-4o using the expert prompt, and writes corrected text
back to the same CSV (in a new 'LLMcorrection' column). Progress is saved after
every row so the script can be safely interrupted and resumed.

Usage:
    python correction/ocr_correction.py --input path/to/BlueBookData.csv
    python correction/ocr_correction.py --input path/to/BlueBookData.csv --model gpt-4o-mini
    python correction/ocr_correction.py --input path/to/BlueBookData.csv --start 500 --end 1000
"""

import argparse
import os
import time

import pandas as pd
from openai import OpenAI

REPO_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_PATH = os.path.join(REPO_ROOT, "prompts", "expert.txt")


def main():
    parser = argparse.ArgumentParser(description="Apply GPT OCR correction to a Blue Book CSV.")
    parser.add_argument("--input",  required=True, help="Path to the BlueBookData CSV.")
    parser.add_argument("--model",  default="gpt-4o", help="OpenAI model to use (default: gpt-4o).")
    parser.add_argument("--start",  type=int, default=0,   help="First row index to process (0-based).")
    parser.add_argument("--end",    type=int, default=None, help="Last row index (exclusive). Defaults to end of file.")
    parser.add_argument("--output", default=None, help="Output CSV path. Defaults to overwriting the input file.")
    args = parser.parse_args()

    api_key = input("OpenAI API key: ").strip()
    client  = OpenAI(api_key=api_key)

    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    df = pd.read_csv(args.input)
    if "LLMcorrection" not in df.columns:
        df["LLMcorrection"] = ""

    end_row    = args.end if args.end is not None else len(df)
    end_row    = min(end_row, len(df))
    output_path = args.output or args.input

    for i in range(args.start, end_row):
        print(f"Row {i + 1} / {end_row}")

        if pd.notna(df.at[i, "LLMcorrection"]) and str(df.at[i, "LLMcorrection"]).strip():
            print("  Already processed — skipping.")
            continue

        ocr_text = df.at[i, "OCRtext"]
        if not isinstance(ocr_text, str) or len(ocr_text.strip()) <= 3:
            continue

        try:
            t0 = time.time()
            response = client.chat.completions.create(
                model=args.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": ocr_text},
                ],
                temperature=0.3,
                timeout=300,
            )
            corrected = response.choices[0].message.content.strip()
            elapsed   = time.time() - t0
            print(f"  Done in {elapsed:.1f}s")
        except Exception as e:
            print(f"  Error: {e}")
            corrected = ""

        df.at[i, "LLMcorrection"] = corrected
        df.to_csv(output_path, index=False)

    print(f"\nSaved to: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()
