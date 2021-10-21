
import time
import json
import http.client
from pathlib import Path
import os
from dotenv import load_dotenv
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
load_key = os.environ['API_KEY']
key = "api_key=" + load_key
conn = http.client.HTTPSConnection("api.uptimerobot.com")
headers = {
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache"
    }

to_add = [] #Add domains as a list to use this in batch.
total_count = len(to_add)

def add_in_batch(to_add):
    current_item = 0
    for monitor in to_add:
        domainwithcache = f'{monitor}/?*cachebuster*'
        adding = f'{key}&format=json&type=1&url=https://{domainwithcache}&friendly_name={monitor}&alert_contacts=0566440_0_0-2706271_0_0-2749984_0_0&timeout=60'
        conn.request("POST", "/v2/newMonitor", adding, headers)
        #print(adding)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        print(data) 
        current_item += 1
        print(f'Added {monitor} successfully {current_item}/{total_count}')
        time.sleep(10)


def add_single(monitor, cluster):
    domainwithcache = f'{monitor}/?*cachebuster*'
    domainwithcluster = f'{monitor} {cluster}'
    adding = f'{key}&format=json&type=1&url=https://{domainwithcache}&friendly_name={domainwithcluster}&alert_contacts=0566440_0_0-2706271_0_0-2749984_0_0&timeout=60'
    conn.request("POST", "/v2/newMonitor", adding, headers)
    print(f'Added {monitor} successfully')