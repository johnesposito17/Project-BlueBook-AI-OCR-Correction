# National ARchives download file using search after should do all files

import requests
import json
import os

# Get API Key from environment variable or user input
APIKey = os.getenv('CATALOG_API_KEY') or input('Enter your API Key: ')

# Set headers with the API key
headers = {
    'x-api-key': APIKey,
}

# Input the parent NAID
naId = input('Enter the Parent NAID: ')

# Initialize searchAfter and other variables
searchAfter = '*'
total_results = 0
page_count = 0
more_pages = True

while more_pages:
    # Perform the GET request with searchAfter pagination
    response = requests.get(f'https://catalog.archives.gov/api/v2/records/search?limit=1000&searchAfter={searchAfter}&availableOnline=true&ancestorNaId={naId}', headers=headers)
    data = response.json()

    # Check if the request was successful
    if response.status_code == 200:
        hits = data['body']['hits']['hits']

        # If no more hits are found, stop pagination
        if not hits:
            more_pages = False
        else:
            total_results += len(hits)
            page_count += 1

            # Get the searchAfter value from the last hit for the next request
            searchAfter = str(hits[-1]['sort'][0])
            print(f'Page {page_count}: Processed {total_results} records, last NAID: {searchAfter}')
            
        if page_count == 10: # Our way of a limiting number of results for testing
            exit()
    else:
        print(f"Error: {response.status_code}")
        more_pages = False

# Print total number of results
print(f'Total records retrieved: {total_results}')
