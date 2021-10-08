#uptime API
# https://uptimerobot.com/api/ ← documentation.

import json
import http.client
import re
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

#Set offset to a range to get ALL. API has a limit of 50 results, this will get up to 400 and return it in a list.
def getinfo(): 
    all_ids = []
    offset_var_add = 0
    for update_offset in range(0,350,50):
        offset_var_full = "offset="+ str(update_offset)
        getinfomonitor = key + "&format=json&logs=1&" + offset_var_full
        conn.request("POST", "/v2/getMonitors", getinfomonitor, headers)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        mydata = json.loads(data)
        loaded_monitors = mydata['monitors']
        for ids in range(len(loaded_monitors)):
            to_add = loaded_monitors[ids]['id']
            all_ids.append(to_add)            
    return all_ids
            
get_monitors = getinfo()

#Edit the monitors one by one. In this case it is only changing the timeout to 60.
def editdomain(get_monitors):
    for monitorid in get_monitors:
        edit = key + "&format=json&id=%s&timeout=60" %(monitorid)
        conn.request("POST", "/v2/editMonitor", edit, headers)
        res = conn.getresponse()
        data = res.read()
        print("Updated", monitorid)

editdomain(get_monitors)