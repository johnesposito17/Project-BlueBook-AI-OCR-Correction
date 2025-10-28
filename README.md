# Study of Post-OCR Correction of Government Documents through LLMs

## TLDR

## Process
- Wrote Python scripts to web scrape thousands of historical documents digitized using OCR (Optical Character Recognition) via National Archives API
- Used 7 LLMs with 3 different prompts to perform comparative study on speed, accuracy, and cost of each prompt-model combination
- Manually transcribed 100 randomly sampled pages of Project Bluebook
- Used modified Levenstein distance to calculate Character Error Rate between Model-Prompt Combo outputs and ground truth transcriptions
  

 ## Related Endevours
- Formal research paper currently in-progress
- One of 4 UW-Madison students nominated to attend US Naval Academy’s 2025 NASEC Conference on AI to present work
- Used Google Looker to make the restored versions of [Project Bluebook]([url](https://sites.google.com/view/project-blue-book-ai-restored/home/)) and [MLK Jr. Files]([url](https://sites.google.com/view/mlk-files-ai-restored/)) searchable for the first time ever.
- Created the [AI Archivist Podcast]([url](https://open.spotify.com/show/5yOR7mBE2mFAtZHlDgKtGa?si=436a5f14ceaa4b90)) to present discuss interesting stories related to MLK Jr. files.
- [Made the Epstein files searchable]([url](https://sites.google.com/view/epstein-extracted/)) albeit using a pipeline that addressed different challenges (the documents themselves were reOCRed entirely as opposed to correcting a preexisting OCR
  
