# Project Blue Book — AI OCR Correction

Restoring 100,000 pages of declassified US Air Force UFO records using large language models.

---

## Overview

Project Blue Book was the US Air Force's systematic study of UFO sightings, running from 1947 to 1969. The National Archives holds over 100,000 pages of the original case files — all digitized, but with OCR (Optical Character Recognition) quality that ranges from passable to completely garbled.

This project uses LLMs to correct those OCR errors at scale, making the full document set searchable for the first time. We evaluated six models across three prompting strategies on 100 hand-transcribed pages to find the best-performing combination, then ran the correction pipeline on the full 57,434-page corpus — making approximately **9.8 million character corrections** across 62 million total characters.

**Results are live and searchable:**
- [Project Blue Book — AI Restored](https://sites.google.com/view/project-blue-book-ai-restored/home/)
- [MLK Jr. Files — AI Restored](https://sites.google.com/view/mlk-files-ai-restored/)
- [Epstein Files — Searchable](https://sites.google.com/view/epstein-extracted/)

**Related work:**
- Research paper recently submitted to Liminia journal of UAP studies
- Accepted to UPenn's National Research Conference to present process and results
- Nominated to share findings at the Naval Academy's NASEC AI Conference
- [AI Archivist Podcast](https://open.spotify.com/show/5yOR7mBE2mFAtZHlDgKtGa) — stories from the MLK Jr. files

---

## Results

Character Error Rate and computation time for all model-prompt pairs. The mean CER between the original OCR and the ground truth for the 100 documents we sampled was **0.276** (std 0.323) — poor enough that even the least effective models were easily able to outperform it. GPT-4o combined with the expert prompt achieved the lowest CER of **0.179** while Gemini 2.5 Flash-Lite with the Wikipedia prompt was the quickest.

<img width="625" height="323" alt="OCR Results Table" src="https://github.com/user-attachments/assets/9faabaa0-bee0-4fa2-938b-10fcd4c81e43" />

> Full per-prompt averages are in `results/`. Run `python evaluation/calculate_averages.py results/<model>_results.csv` to regenerate them.

### Document type breakdown

The overall mean CER masks a strongly bimodal distribution. The 100-page sample spans six document categories with very different baseline difficulty and different amenability to LLM correction:

| Document Type | N | Baseline CER | GPT-4o Expert CER | Reduction |
|---|---|---|---|---|
| Form | 53 | 0.255 | 0.120 | −53% |
| Memo | 30 | 0.208 | 0.140 | −33% |
| Article | 6 | 0.448 | 0.342 | −24% |
| Summary Table | 3 | 0.159 | 0.198 | +24% |
| Image/Map | 7 | 0.670 | 0.657 | −2% |

**Forms** (53% of the sample) benefit most from the expert prompt — structured fields give the model strong anchors. **Memos** are single-column body text and are the easiest category for every model. **Image/Map** pages contain no transcribable text; CER hovers near 1.0 regardless of model and these pages account for most of the distribution's upper tail. **Newspaper articles** are the second-hardest: multi-column layouts and varied typesetting confuse OCR severely and LLMs only partially recover them. Excluding Image/Map pages, the text-bearing documents have a baseline CER of 0.238 and GPT-4o (expert) brings that to 0.135.

Full per-type statistics and long-form NAID-level data: [`results/type_analysis.md`](results/type_analysis.md) · [`results/type_cer_detail.csv`](results/type_cer_detail.csv)

## Cost Breakdown

Correcting the full 57,434-page corpus costs between **$9.03** (Gemini 2.5 Flash-Lite) and **$266.78** (GPT-4o) — a 30× price differential for roughly comparable output quality on text-bearing pages. DeepSeek is the cheapest non-Google option. Gemini carries a list price comparable to GPT-4o Mini, but Google provides a $250 developer credit, making it effectively free for projects of this scale.

<img width="634" height="499" alt="Cost Breakdown Table" src="https://github.com/user-attachments/assets/1f7b82ad-4620-43ed-b4f8-f415582f432f" />

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
    ├── type_analysis.md           Per-document-type CER breakdown (Forms, Memos, etc.)
    ├── type_cer_detail.csv        Long-form CER data by NAID × model × prompt × type
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
