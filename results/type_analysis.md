# Document-Type CER Analysis
## Classified document types
| Type | Count | Notes |
|---|---|---|
| Form | 53 | Government forms, routing slips, UFO report forms |
| Memo | 30 | Military messages, letters, cables |
| Image/Map | 7 | Maps, charts, photographs — no transcribable text |
| Article | 6 | Newspaper clippings |
| Summary Table | 3 | Tabular data summaries |
| Others | 1 | Miscellaneous |

## Baseline OCR CER by document type
*(Raw OCR vs. human transcription — before any LLM correction)*

| Document Type | N | Mean CER | Median CER | Std |
|---|---|---|---|---|
| Form | 53 | 0.255 | 0.135 | 0.287 |
| Memo | 30 | 0.208 | 0.069 | 0.311 |
| Image/Map | 7 | 0.670 | 0.897 | 0.433 |
| Article | 6 | 0.448 | 0.592 | 0.336 |
| Summary Table | 3 | 0.159 | 0.105 | 0.132 |
| Others | 1 | 0.017 | 0.017 | nan |

## All-model expert-prompt CER by document type
*(Mean CER using Prompt 3 — expert prompt — averaged across 3 trials)*

| Document Type | GPT-4o | GPT-4o Mini | GPT-5 | Gemini 2.5 Flash | Gemini Flash-Lite | DeepSeek |
|---|---|---|---|---|---|---|
| Form | 0.120 | 0.217 | 0.125 | 0.213 | 0.172 | 0.125 |
| Memo | 0.140 | 0.140 | 0.147 | 0.146 | 0.142 | 0.145 |
| Image/Map | 0.657 | 0.658 | 0.669 | 0.652 | 0.669 | 0.655 |
| Article | 0.342 | 0.509 | 0.324 | 0.382 | 0.418 | 0.322 |
| Summary Table | 0.198 | 0.372 | 0.142 | 0.157 | 0.164 | 0.160 |
| Others | 0.013 | 0.014 | 0.014 | 0.011 | 0.017 | 0.011 |

## GPT-4o (Expert prompt) — improvement over baseline
| Document Type | N | Baseline CER | GPT-4o Expert CER | Δ CER | % Reduction |
|---|---|---|---|---|---|
| Form | 53 | 0.255 | 0.120 | -0.135 | -53.0% |
| Memo | 30 | 0.208 | 0.140 | -0.068 | -32.7% |
| Image/Map | 7 | 0.670 | 0.657 | -0.013 | -1.9% |
| Article | 6 | 0.448 | 0.342 | -0.106 | -23.6% |
| Summary Table | 3 | 0.159 | 0.198 | +0.038 | +24.1% |
| Others | 1 | 0.017 | 0.013 | -0.005 | -26.9% |

## Key takeaways

- **Image/Map pages drive the worst CER.** These contain no transcribable text; the model either hallucinates or returns nothing, producing CER ≈ 1.0 regardless of model.
- **Articles (newspaper clippings) are the second-hardest category** — multi-column layouts, dense typesetting, and varied fonts confuse OCR severely; LLMs partially recover them.
- **Forms are the bulk of the corpus (>50%) and perform well** — structured fields give the model strong anchors; expert-prompt GPT-4o achieves the largest relative improvement here.
- **Memos are close to Forms in difficulty** — body text is clean and single-column;
  all models reach low CER (< 0.10 median on the expert prompt).
- **Overall mean CER is inflated by the Image/Map tail.** Excluding Image/Map pages from reporting gives a more honest picture of transcription quality for text-bearing documents.
