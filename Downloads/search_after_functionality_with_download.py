import requests
import pandas as pd
import os

# === Get API Key ===
APIKey = os.getenv('CATALOG_API_KEY') or input('Enter your API Key: ')

headers = {
    'x-api-key': APIKey,
    'Content-Type': 'application/json'
}

# === Project Blue Book Parent NAID ===
naId = "597821"
searchAfter = '*'
total_results = 0
page_count = 0
more_pages = True
records = []

print(f"🔎 Starting searchAfter pagination for Parent NAID: {naId}")

# === searchAfter: Get all child records ===
while more_pages:
    url = f'https://catalog.archives.gov/api/v2/records/search?limit=1000&searchAfter={searchAfter}&availableOnline=true&ancestorNaId={naId}'
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        break

    data = response.json()
    hits = data['body']['hits']['hits']

    if not hits:
        break

    for hit in hits:
        naid = hit.get('_id')
        title = hit['_source']['record'].get('title', '')
        records.append({'NAID': naid, 'title': title})

    total_results += len(hits)
    page_count += 1
    searchAfter = str(hits[-1]['sort'][0])

    print(f"📄 Page {page_count}: Total records so far = {total_results}, last NAID = {searchAfter}")

print(f"\n📦 Retrieved {len(records)} child records under Parent NAID {naId}")

# === Convert to DataFrame ===
doc_list = pd.DataFrame(records)

if 'NAID' in doc_list.columns and not doc_list.empty:
    doc_list = doc_list.sort_values('NAID').reset_index(drop=True)
    print(f"📥 Loaded {len(doc_list)} documents.")
else:
    print("❌ No valid records found.")
    exit()

# === Initialize output ===
bluebook_rows = []
file_counter = 0
max_files = 500  # ✅ Download limit for testing

# === Loop over NAIDs and download files ===
for i, row in doc_list.iterrows():
    if file_counter >= max_files:
        print(f"\n⚠️ Reached download cap of {max_files} files. Stopping download.")
        break

    naid = row['NAID']
    title = row['title']
    print(f"\n📂 Processing NAID {naid}: {title}")

    url = f'https://catalog.archives.gov/api/v2/records/search?naId={naid}&includeExtractedText=true&includeTranscriptions=true'
    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        print(f"  ❌ Failed to fetch record {naid}, status {resp.status_code}")
        continue

    data = resp.json()
    hits = data['body']['hits']['hits']
    if not hits:
        continue

    try:
        digital_objects = hits[0]['_source']['record']['digitalObjects']
        print(f"  📄 Found {len(digital_objects)} digital objects.")
    except KeyError:
        digital_objects = []
        print("  ⚠️ No digitalObjects found.")

    for dobj in digital_objects:
        if file_counter >= max_files:
            print(f"\n⚠️ Reached download cap of {max_files} files inside loop.")
            break

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

    # === Retrieve human transcriptions ===
    url_transcript = f"https://catalog.archives.gov/api/v2/transcriptions/naId/{naid}"
    resp_trans = requests.get(url_transcript, headers=headers)
    if resp_trans.status_code != 200:
        print(f"  ❌ Failed transcription request, status {resp_trans.status_code}")
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

# === Save results to CSV ===
output_path = "/Users/johnesposito/Documents/Summer 2025 Code/National Archives Download/BlueBookData.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

BlueBookTable = pd.DataFrame(bluebook_rows)
BlueBookTable.to_csv(output_path, index=False)

print(f"\n✅ Saved {file_counter} files to {output_path}")

# === To download all 10,622 files later ===
# Just comment out or remove:
# if file_counter >= max_files:
#     break
