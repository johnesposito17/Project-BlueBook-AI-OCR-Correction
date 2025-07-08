import pandas as pd
import os
import time
from openai import OpenAI
from openai.types.chat import ChatCompletion

# path names configured incorrectly
# won't work until we have the csv pushed onto the git

# === 1. Setup OpenAI client ===
api_key = "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"
client = OpenAI(api_key=api_key)

# === 2. Load system prompt from text file ===
prompt_path = "/Users/johnesposito/Documents/Summer 2025 Code/OAI API Integration/BlueBook_complex_prompt.txt"
if not os.path.exists(prompt_path):
    raise FileNotFoundError(f"System prompt file not found: {prompt_path}")

with open(prompt_path, "r", encoding="utf-8") as f:
    system_prompt = f.read()

# === 3. Load your CSV into a DataFrame ===
df = pd.read_csv("/Users/johnesposito/Documents/Summer 2025 Code/National Archives Download/BlueBookData.csv")

# Ensure the LLMcorrection column exists
if "LLMcorrection" not in df.columns:
    df["LLMcorrection"] = ""

# === 4. Define function to call GPT ===
def correct_ocr_text(ocr_text: str) -> str:
    try:
        if isinstance(ocr_text, str) and len(ocr_text.strip()) > 3:
            response: ChatCompletion = client.chat.completions.create(
                model="gpt-4o",  # or "gpt-4o-mini" if preferred
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": ocr_text}
                ],
                temperature=0.3,  # Low temperature for consistency
                timeout=300  # seconds
            )
            return response.choices[0].message.content.strip()
        else:
            return ""
    except Exception as e:
        print(f"Error processing OCR text: {e}")
        return ""

# === 5. Process a range of rows ===
start_row = 0
end_row = 10

end_row = min(end_row, len(df))

for i in range(start_row, end_row):
    print(f"Processing row {i + 1} of {len(df)}")
    if pd.isna(df.at[i, "LLMcorrection"]) or df.at[i, "LLMcorrection"] == "":
        ocr_text = df.at[i, "OCRtext"]
        start_time = time.time()
        corrected = correct_ocr_text(ocr_text)
        elapsed = time.time() - start_time
        print(f"Response time: {elapsed:.2f} seconds")
        df.at[i, "LLMcorrection"] = corrected
    else:
        print("Already processed. Skipping...")

# === 6. Save the updated CSV ===
output_path = os.path.abspath("BlueBookDataWithOCRCorrection.csv")
df.to_csv(output_path, index=False)
print(f"✅ Saved to: {output_path}")

