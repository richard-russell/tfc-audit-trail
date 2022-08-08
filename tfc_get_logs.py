import os
import requests
import time

POLL_INTERVAL = 60  # seconds to wait between API calls
PAGESIZE = None     # number of events to fetch with each call (None = default)
TFC_ORG_TOKEN = os.environ.get('TFC_ORG_TOKEN')
TFC_LOG_SINK = os.environ.get('TFC_LOG_SINK')
AUDIT_TRAIL_URL = "https://app.terraform.io/api/v2/organization/audit-trail"

tfc_headers = { "Authorization": f"Bearer {TFC_ORG_TOKEN}"}
logstash_headers = { 'content-type': 'application/json'}
url_params = {'since': None, 'page[size]': PAGESIZE}

def get_events(URL, headers, params, page=1):
    """Call audit trail API and return the events.
       Handle pagination through recursion.
       JSON payload should contain 'events' and 'pagination' at the top level.
    """
    params['page'] = None if page == 1 else page
    r = requests.get(URL, headers=headers, params=params)
    r.raise_for_status()
    json_response = r.json()
    events = json_response['data']
    next_page = json_response['pagination']['next_page']
    if not next_page:
        return events
    return events + get_events(URL, headers, params, page=next_page)

# Main loop
while True:
    events = get_events(AUDIT_TRAIL_URL, headers=tfc_headers, params=url_params)

    if events:
        url_params['since'] = events[0]['timestamp']
        for event in events:
            print(event)
            if TFC_LOG_SINK:
                rp = requests.post(TFC_LOG_SINK, json=event, headers=logstash_headers)

    time.sleep(POLL_INTERVAL)
