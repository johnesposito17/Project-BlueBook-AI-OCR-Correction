# Study of Post-OCR Correction of Government Documents using LLMs

## TLDR
We used LLMs to restore low quality OCR (Optical Character Recognition) of over 100,000 historical documents on the National Archives website and made the restored versions searchable on Google Looker.

## Process
- Wrote Python scripts to web scrape thousands of historical documents digitized using OCR (Optical Character Recognition) via National Archives API
- Wrote scripts to correct errors in the files using Open AI, Gemini, and Deepseek APIs
- Used 7 different models with 3 different prompts to perform comparative study on speed, accuracy, and cost of each prompt-model combination
- Manually transcribed 100 randomly sampled pages of Project Bluebook
- Used modified Levenstein distance to calculate Character Error Rate between Model-Prompt Combo outputs and ground truth transcriptions
  

 ## Related Endeavours
- Formal research paper currently in-progress
- One of 4 UW-Madison students nominated to attend US Naval Academy’s 2025 NASEC Conference on AI to present work
- Used Google Looker to make the restored versions of [Project Bluebook](https://sites.google.com/view/project-blue-book-ai-restored/home/) and [MLK Jr. Files](https://sites.google.com/view/mlk-files-ai-restored/) searchable for the first time ever.
- Created the [AI Archivist Podcast](https://open.spotify.com/show/5yOR7mBE2mFAtZHlDgKtGa?si=7776ad36385c4f30) discussing interesting stories related to MLK Jr. files.
- [Made the Epstein files searchable](https://sites.google.com/view/epstein-extracted/) albeit using a pipeline that addressed different challenges (the documents themselves were reOCRed entirely as opposed to correcting a preexisting OCR)


## Results

Character Error Rate and Computation Time for all model-prompt pairs.  The mean CER between the original OCR and the ground truth for the 100 documents we sampled was 0.276, with a standard deviation of 0.323, which even some of the least effective models were easily able to outperform.  GPT 4o combined with the expert prompt (highlighted in green) acheived the lowest CER while Gemini 2.5 Flash-Lite with the Wikipedia prompt was the quickest.
 

<img width="625" height="323" alt="OCR Results Table" src="https://github.com/user-attachments/assets/9faabaa0-bee0-4fa2-938b-10fcd4c81e43" />

## Cost Breakdown

The cheapest model option was found to be DeepSeek, and the most expensive was GPT-4o.  Gemini was relatively expensive as well (with $0.30 per 1M input tokens and $2.50 per 1M output); however, Google provides a $250 credit to developers, and so for our purposes, they are essentially free.

<img width="634" height="499" alt="Cost Breakdown Table 2" src="https://github.com/user-attachments/assets/1f7b82ad-4620-43ed-b4f8-f415582f432f" />

