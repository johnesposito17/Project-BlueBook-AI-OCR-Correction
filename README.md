# Project Blue Book — AI OCR Correction

Restoring 100,000 pages of declassified US Air Force UFO records using large language models.

---

## Overview

Project Blue Book was the US Air Force's systematic study of UFO sightings, running from 1947 to 1969. The National Archives holds over 100,000 pages of the original case files — all digitized, but with OCR (Optical Character Recognition) quality that ranges from passable to completely garbled.

This project uses LLMs to correct those OCR errors at scale, making the full document set searchable for the first time. We evaluated six models across three prompting strategies on 100 hand-transcribed pages to find the best-performing combination before running the correction pipeline on the entire corpus.

**Results are live and searchable:**
- [Project Blue Book — AI Restored](https://sites.google.com/view/project-blue-book-ai-restored/home/)
- [MLK Jr. Files — AI Restored](https://sites.google.com/view/mlk-files-ai-restored/)
- [Epstein Files — Searchable](https://sites.google.com/view/epstein-extracted/)

**Related work:**
- Formal research paper in progress
- Presented at the US Naval Academy's NASEC 2025 Conference on AI (one of four UW–Madison nominees)
- [AI Archivist Podcast](https://open.spotify.com/show/5yOR7mBE2mFAtZHlDgKtGa) — stories from the MLK Jr. files

---

## Results

We manually transcribed 100 randomly sampled pages to create a ground truth dataset. Character Error Rate (CER) measures edit distance between corrected text and that ground truth — lower is better, 0 is a perfect match.

**Baseline:** The raw OCR had a mean CER of **0.276 ± 0.323** against human transcriptions — poor enough that even the weakest models showed meaningful improvement.

| Model | Prompt | Avg CER | Avg Time (s) |
|---|---|---|---|
| **GPT-4o** | **Expert** | **lowest** | — |
| GPT-4o | Wikipedia Context | — | — |
| GPT-4o | Basic | — | — |
| GPT-4o Mini | Expert | — | — |
| GPT-5 | Expert | — | — |
| Gemini 2.5 Flash | Expert | — | — |
| Gemini 2.5 Flash-Lite | Wikipedia Context | — | fastest |
| DeepSeek Chat | Expert | — | — |

> Full per-prompt averages are in `results/`. Run `python evaluation/calculate_averages.py results/<model>_results.csv` to regenerate them.

**Cost:** DeepSeek was cheapest per token; GPT-4o was most expensive. Gemini carried a ~$0.30/1M input token cost but Google's $250 developer credit made it effectively free for this project.

---

## Repository Structure

```
├── data/
│   ├── download_from_archives.py   Download all Blue Book records via National Archives API
│   └── human_transcriptions.csv   100 hand-transcribed pages used as ground truth
│
├── prompts/
│   ├── basic.txt                  Minimal: "fix the OCR errors, return only corrected text"
│   ├── wikipedia_context.txt      Basic prompt + Blue Book background for domain context
│   └── expert.txt                 Full expert prompt: layout rules, form reordering, special chars
│
├── correction/
│   └── ocr_correction.py          Apply LLM correction to the full dataset
│
├── evaluation/
│   ├── run_evaluation.py          Full 3-prompt × 3-trial evaluation for any single model
│   ├── run_multimodel.py          Quick side-by-side comparison of multiple models on select pages
│   ├── calculate_averages.py      Compute per-prompt CER/time averages from a results CSV
│   ├── compare_ocr_vs_human.py    Compute baseline CER between raw OCR and human transcriptions
│   └── string_comparison.py       CER implementation (Levenshtein distance)
│
└── results/
    ├── ocr_baseline_cer.csv       Raw OCR vs. human CER for all 100 test pages
    ├── gpt4o_results.csv          GPT-4o: 3 prompts × 3 trials × 100 pages
    ├── gpt4o_mini_results.csv     GPT-4o Mini results
    ├── gpt5_results.csv           GPT-5 results
    ├── gemini_flash_results.csv   Gemini 2.5 Flash results
    ├── gemini_flash_lite_results.csv  Gemini 2.5 Flash-Lite results
    └── deepseek_results.csv       DeepSeek Chat results
```

---

## Setup

```bash
git clone https://github.com/johnesposito17/Project-BlueBook-AI-OCR-Correction.git
cd Project-BlueBook-AI-OCR-Correction
pip install -r requirements.txt
```

API keys are entered interactively when you run each script — never hardcode them or commit them to the repo.

---

## Usage

### 1. Download the Blue Book dataset

```bash
python data/download_from_archives.py
# Prompts for your National Archives API key
# Outputs: BlueBookData.csv  (~100,000 rows)
```

Free API keys are available at [catalog.archives.gov](https://catalog.archives.gov/api/v2/).

### 2. Compute the baseline (raw OCR vs. human)

```bash
python evaluation/compare_ocr_vs_human.py
# Reads:  data/human_transcriptions.csv
# Writes: results/ocr_baseline_cer.csv
```

### 3. Run the full evaluation for a model

```bash
python evaluation/run_evaluation.py --model gpt-4o
python evaluation/run_evaluation.py --model gemini-2.5-flash
python evaluation/run_evaluation.py --model deepseek-chat
```

Supported models: `gpt-4o`, `gpt-4o-mini`, `gpt-5`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `deepseek-chat`

Each run produces `results/<model>_results.csv` with CER and processing time for all 3 prompts × 3 trials × 100 pages. Progress is saved after every row so runs can be safely interrupted and resumed.

### 4. Summarize results by prompt

```bash
python evaluation/calculate_averages.py results/gpt4o_results.csv
```

### 5. Quick multi-model spot check

Edit `MODELS` and `NAIDS_TO_PROCESS` at the top of the script, then:

```bash
python evaluation/run_multimodel.py
```

### 6. Correct the full dataset

```bash
# Full run with the best-performing combination
python correction/ocr_correction.py --input /path/to/BlueBookData.csv --model gpt-4o

# Process a specific row range (useful for parallelizing)
python correction/ocr_correction.py --input /path/to/BlueBookData.csv --start 5000 --end 10000
```

---

## The Three Prompts

| File | Strategy |
|---|---|
| `basic.txt` | One sentence: correct OCR errors, return only the corrected text. Lowest latency. |
| `wikipedia_context.txt` | Adds a paragraph explaining Project Blue Book so the model understands the domain. Helps on degraded pages with jargon. |
| `expert.txt` | Full prompt covering: multi-column newspaper layouts, filled government form reordering (field titles vs. field data), abbreviation preservation, long alphanumeric codes, selected-checkbox notation (`ʘ`), margin notes, and page numbers. Best overall CER. |

---

## How CER Is Computed

```
CER = Levenshtein_distance(corrected, ground_truth) / max(len(corrected), len(ground_truth))
```

Before comparison, both strings are: lowercased, line breaks collapsed to spaces, special correction markers (`ǂ...ǂ`, `ʘ...ʘ`) resolved, and em/en dashes normalized to hyphens. See `evaluation/string_comparison.py` for the full implementation.
