import os
import requests
import time

POLL_INTERVAL = 10
TFC_ORG_TOKEN = os.environ.get('TFC_ORG_TOKEN')
AUDIT_TRAIL_URL = "https://app.terraform.io/api/v2/organization/audit-trail"

headers = { "Authorization": f"Bearer {TFC_ORG_TOKEN}"}

# r = requests.get(AUDIT_TRAIL_URL, headers = headers)

url_params = {'since': None}

while True:
    r = requests.get(AUDIT_TRAIL_URL, headers=headers, params=url_params)
    r.raise_for_status()

    json_response = r.json()
    events = json_response['data']

    if events:
        url_params['since'] = json_response['data'][0]['timestamp']
        for event in events:
            print(event)

    time.sleep(POLL_INTERVAL)

