import requests
import pandas as pd
import os

# This file downloads the NAID, title, OCR, and human transcription for only the first file unit of the JFK Assasination Documents



# API key and headers
NA_api_key = "lZMcWgU1LR3sZ7ZNDlxqN61BWdGAVJpN51oDI1RQ"
headers = {
    "Content-Type": "application/json",
    "x-api-key": NA_api_key
}

# Get list of all Blue Book NAIDs
url_NAIDlist = "https://catalog.archives.gov/api/v2/records/parentNaId/641323?limit=10000"
response = requests.get(url_NAIDlist, headers=headers)
response.raise_for_status()
data = response.json()
hits = data['body']['hits']['hits']

# Extract NAID and title into a DataFrame
records = []
for item in hits:
    naid = item.get('_id')
    if not naid:
        continue
    title = item['_source']['record'].get('title', '')
    records.append({'NAID': naid, 'title': title})

doc_list = pd.DataFrame(records)

if 'NAID' in doc_list.columns and not doc_list.empty:
    doc_list = doc_list.sort_values('NAID').reset_index(drop=True)
    print(f"📥 Loaded {len(doc_list)} documents.")
else:
    print("❌ No valid records with NAID found.")
    exit()

# Initialize output list and file counter
bluebook_rows = []
file_counter = 0

# Loop over records
for i, row in doc_list.iloc[:].iterrows():
    naid = row['NAID']
    title = row['title']
    print(f"\n📂 Processing NAID {naid}: {title}")

    url = f'https://catalog.archives.gov/api/v2/records/search?naId={naid}&includeExtractedText=true&includeTranscriptions=true'
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"  ❌ Failed for NAID {naid}, status {resp.status_code}")
        continue

    data = resp.json()
    hits = data['body']['hits']['hits']
    print(f"  ✅ Found {len(hits)} hits.")

    if not hits:
        continue

    try:
        digital_objects = hits[0]['_source']['record']['digitalObjects']
        print(f"  📄 Found {len(digital_objects)} digital objects.")
    except KeyError:
        digital_objects = []
        print("  ⚠️ No digitalObjects found.")

    for dobj in digital_objects:
        obj_id = dobj.get('objectId', '')
        obj_url = dobj.get('objectUrl', '')
        ocr_text = dobj.get('extractedText', '')

        bluebook_rows.append({
            'ParentNAID': naid,
            'title': title,
            'NAID': obj_id,
            'imageURLs': obj_url,
            'OCRtext': ocr_text,
            'HumanText': ''
        })

        file_counter += 1
        print(f"    🧾 Saved file #{file_counter}: {obj_id}")

    # Retrieve human transcriptions
    url_transcript = f"https://catalog.archives.gov/api/v2/transcriptions/naId/{naid}"
    resp_trans = requests.get(url_transcript, headers=headers)
    if resp_trans.status_code != 200:
        print(f"  ❌ Failed transcriptions for NAID {naid}, status {resp_trans.status_code}")
        continue

    data_trans = resp_trans.json()
    trans_hits = data_trans['body']['hits']['hits']
    print(f"  📝 Found {len(trans_hits)} transcriptions.")

    for t in trans_hits:
        human_text = t['_source']['record'].get('contribution', '')
        transcript_id = t['_source']['record'].get('target', {}).get('objectId', '')
        for row_dict in bluebook_rows:
            if row_dict['NAID'] == transcript_id:
                row_dict['HumanText'] = human_text

# Save results to CSV
output_path = "/Users/johnesposito/Documents/Summer 2025 Code/National Archives Download/JFKData.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

BlueBookTable = pd.DataFrame(bluebook_rows)
BlueBookTable.to_csv(output_path, index=False)

print(f"\n✅ Saved {file_counter} files to JFKData.csv")
