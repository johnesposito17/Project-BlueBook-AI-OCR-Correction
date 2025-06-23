import requests
import pandas as pd

NA_api_key = "lZMcWgU1LR3sZ7ZNDlxqN61BWdGAVJpN51oDI1RQ"
headers = {
    "Content-Type": "application/json",
    "x-api-key": NA_api_key
}


url_NAIDlist = "https://catalog.archives.gov/api/v2/records/parentNaId/597821?limit=10000"

response = requests.get(url_NAIDlist, headers=headers)
response.raise_for_status()  # raise error if bad response

data = response.json()

# Extract relevant part of JSON
hits = data['body']['hits']['hits']
import json
print("Sample record structure:\n", json.dumps(hits[0], indent=2))


# Build a DataFrame with NAID and title
records = []
for item in hits:
    # naid = item['x_id']
    naid = item.get('_id')
    if not naid:
        continue  # skip this item if no NAID is present
    title = item['_source']['record'].get('title', '')
    records.append({'NAID': naid, 'title': title})

doc_list = pd.DataFrame(records)

doc_list = pd.DataFrame(records)

if 'NAID' in doc_list.columns and not doc_list.empty:
    doc_list = doc_list.sort_values('NAID').reset_index(drop=True)
else:
    print("No valid records with NAID found.")
    exit()


bluebook_rows = []

for i, row in doc_list.iterrows():
    naid = row['NAID']
    title = row['title']

    url = f'https://catalog.archives.gov/api/v2/records/search?naId={naid}&includeExtractedText=true&includeTranscriptions=true'

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Failed for NAID {naid}, status {resp.status_code}")
        continue
    data = resp.json()

    hits = data['body']['hits']['hits']
    if not hits:
        continue

    # Typically digitalObjects lives inside the first hit
    try:
        digital_objects = hits[0]['_source']['record']['digitalObjects']
    except KeyError:
        digital_objects = []

    for dobj in digital_objects:
        # Handle case if dobj is dict or list element
        obj_id = dobj.get('objectId', '')
        obj_url = dobj.get('objectUrl', '')
        ocr_text = dobj.get('extractedText', '')

        bluebook_rows.append({
            'ParentNAID': naid,
            'title': title,
            'NAID': obj_id,
            'imageURLs': obj_url,
            'OCRtext': ocr_text,
            'HumanText': ''  # fill later
        })

    # Now get transcriptions for this NAID
    url_transcript = f"https://catalog.archives.gov/api/v2/transcriptions/naId/{naid}"
    resp_trans = requests.get(url_transcript, headers=headers)
    if resp_trans.status_code != 200:
        print(f"Failed transcriptions for NAID {naid}, status {resp_trans.status_code}")
        continue
    data_trans = resp_trans.json()
    trans_hits = data_trans['body']['hits']['hits']

    # Map transcript text to NAID of digital object
    for t in trans_hits:
        human_text = t['_source']['record'].get('contribution', '')
        transcript_id = t['_source']['record'].get('target', {}).get('objectId', '')

        # Find matching rows by NAID
        for row_dict in bluebook_rows:
            if row_dict['NAID'] == transcript_id:
                row_dict['HumanText'] = human_text

BlueBookTable = pd.DataFrame(bluebook_rows)
BlueBookTable.to_csv("BlueBookData.csv", index=False)
print("Saved BlueBookData.csv")
