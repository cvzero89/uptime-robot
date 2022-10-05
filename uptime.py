## - UptimeRobot API
## - Documentation → https://uptimerobot.com/api/
## - https://github.com/cvzero89/uptime-robot

import json
import http.client
import re
from pathlib import Path
import os
from dotenv import load_dotenv

apikey = None

## - Loading the key from .env. If it does not exist it will ask to enter it manually.

def loadkey():
    try:
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)
        load_key = os.environ['API_KEY']
        return load_key
    except:
        print('Could not find .env file.')
    load_key = None
    while True:
        if load_key == None:
            load_key = input('API key is missing on the .env file. Enter it manually: ')
        break
    return load_key

## - Loading the contacts from .env. If it does not exist it will ask to enter it manually. 
## - It will assume contacts with recurrence _0_0.

def loadcontacts():
    try:
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)
        contacts = os.environ['CONTACTS']
        contact_1 = []
        for contact in contacts.split('|'):
            contact_1.append(f'{contact}_0_0')
        alert_contacts = '-'.join(contact_1)
        return alert_contacts
    except:
        print('Could not find .env file.')
    contacts = None
    while True:
        if contacts == None:
            contacts = input('No contacts were found. Set your alert contacts: ')
            contact_1 = []
            for contact in contacts.split('|'):
                contact_1.append(f'{contact}_0_0')
            alert_contacts = '-'.join(contact_1)
        break
    return alert_contacts

conn = http.client.HTTPSConnection("api.uptimerobot.com")

headers = {
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache"
    }

class Monitor:
    def __init__(self, domain, friendlyName='blank', monitorId=None, type_='1', alert_contacts='blank', monitorInterval='300', monitorTimeout='60', monitorSSL='1'):
        self.type_ = type_
        self.domain = domain.replace('http://', '').replace('https://', '')
        self.friendlyName = friendlyName.replace(' ','')
        self.monitorInterval = monitorInterval
        self.monitorTimeout = monitorTimeout
        self.monitorSSL = monitorSSL
        self.monitorId = monitorId
        self.alert_contacts = alert_contacts.replace('{', '').replace('}', '')

## - Format to print information from the other functions.

    def printInfo(monitor_info):
        print(f'Displaying {len(monitor_info)} records.\n')
        for info in monitor_info:
            monitor = Monitor(*info)
            print(f'Domain name: {monitor.domain}\nFriendly Name: {monitor.friendlyName}\nID: {monitor.monitorId}\n')

## - Edit domains. Needs to be feed a list in monitor_info and option_to_edit to be valid based on https://uptimerobot.com/api/.

    def editdomain(monitor_info, apikey, headers, option_to_edit):
        for info in monitor_info:
            monitor = Monitor(*info)
            edit = f'api_key={apikey}&format=json&id={monitor.monitorId}&{option_to_edit}'
            conn.request("POST", "/v2/editMonitor", edit, headers)
            res = conn.getresponse()
            data = res.read()
            catchRateError(data)
            try:
                mydata = json.loads(data)
            except ValueError:
                print('Could not load JSON data.')
                break
                exit()
            if mydata['stat'] == 'ok':
                print(f'Updated {monitor.friendlyName} successfully!')
            else:
                print(f'Update for {monitor.friendlyName} failed! Error: \n{mydata}')
                print('The option to edit must follow the API documentation at: https://uptimerobot.com/api/.')

## - Add domains. Needs the monitor and alert contacts to have been set.
    
    def add_single(self, apikey, headers, alert_contacts):
        adding = f'api_key={apikey}&format=json&type={self.type_}&url=https://{self.domain}&friendly_name={self.friendlyName}&alert_contacts={alert_contacts}&timeout=60'
        conn.request("POST", "/v2/newMonitor", adding, headers)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        catchRateError(data)
        try:
            mydata = json.loads(data)
        except ValueError:
            print('Could not load JSON data.')
            exit()
        if mydata['stat'] == 'ok':
            print(f'Added {self.friendlyName} successfully!')
        else:
            print(f'Adding {self.friendlyName} failed! Error: \n{mydata}')

## - Search monitors FriendlyName and URL. It can retrieve partial hits. Also used to retrieve ids for mass edits.

    def searchMonitor(self, apikey, headers):
        monitor_info = []
        getinfomonitor = f'api_key={apikey}&format=json&search={self.domain}&logs=1'
        conn.request("POST", "/v2/getMonitors", getinfomonitor, headers)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        catchRateError(data)
        try:
            mydata = json.loads(data)
        except ValueError:
            print('Could not load JSON data.')
            exit()
        if mydata['stat'] == 'ok':
            loaded_monitors = mydata['monitors']
            for ids in range(len(loaded_monitors)):
                to_add = loaded_monitors[ids]['url'], loaded_monitors[ids]['friendly_name'], loaded_monitors[ids]['id']
                monitor_info.append(to_add)
        else:
            print(f'Failed to retrieve monitor list \nError:')
            print(mydata)  
        if not monitor_info:
            print('Monitor info was empty.')
            exit()
        else:
            return monitor_info

## - Set offset to a range to get ALL. API has a limit of 50 results, this will get a default of 150 and return it in a list.

    def getinfo(headers, apikey): 
        monitor_info = []
        offset_var_add = 0
        try:
            offset = int(input('How many records do you want to display?: '))
            offset_range = offset - 50
            if offset_range <= 50:
                offset_range = 50
        except ValueError:
            offset_range = 100
            print('Invalid input, max. 150 records will be displayed.')
        for update_offset in range(0, offset_range,50):
            offset_var_full = f'offset={str(update_offset)}'
            getinfomonitor = f'api_key={apikey}&format=json&logs=0&{offset_var_full}'
            conn.request("POST", "/v2/getMonitors", getinfomonitor, headers)
            res = conn.getresponse()
            data = res.read().decode('utf-8')
            catchRateError(data)
            try:
                mydata = json.loads(data)
            except ValueError:
                print('Could not load JSON data.')
                break
                exit()
            if mydata['stat'] == 'ok':
                loaded_monitors = mydata['monitors']
                for ids in range(len(loaded_monitors)):
                    to_add = loaded_monitors[ids]['url'], loaded_monitors[ids]['friendly_name'], loaded_monitors[ids]['id']
                    monitor_info.append(to_add)
            else:
                print(f'Failed to retrieve monitor list \nError:')
                print(mydata)            
        return monitor_info

## - Imports monitors from a CSV file, needs to be named uptimeimport.csv on the script directory. Executes add_single to add.

    def add_in_batch(headers, apikey):
        import csv
        import time
        current_item = 1
        with open('uptimeimport.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                print(f'Current monitor {current_item}')
                monitor = Monitor(row['URL/IP'], row['Friendly Name'], None, row['Type'], row['Alert Contact'])
                monitor.add_single(apikey, headers, alert_contacts)
                current_item += 1
                time.sleep(2)

## - Delete monitors, used with searchMonitor.

    def deleteMonitor(monitor_info, apikey, headers):
        for info in monitor_info:
            monitor = Monitor(*info)
        delete = f'api_key={apikey}&format=json&id={monitor.monitorId}'                 
        conn.request("POST", "/v2/deleteMonitor", delete, headers)            
        res = conn.getresponse()
        data = res.read()
        catchRateError(data)
        mydata = json.loads(data)
        if mydata['stat'] == 'ok':
            print(f'Monitor {monitor.friendlyName} deleted successfully!')
        else:
            print(f'Could not delete {monitor.friendlyName}. Error: \n{mydata}')

## - Retrieves URL, friendlyName and ID for paused monitors.

    def getPaused(apikey, headers):
        monitor_info = []
        paused = f'api_key={apikey}&format=json&statuses=0'
        conn.request("POST", "/v2/getMonitors/", paused, headers)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        catchRateError(data)
        mydata = json.loads(data)
        if mydata['stat'] == 'ok':
            print('Received paused list.')
            loaded_monitors = mydata['monitors']
            print(f'Number of monitors down: {len(loaded_monitors)}')
            for ids in range(len(loaded_monitors)):
                to_add = loaded_monitors[ids]['url'], loaded_monitors[ids]['friendly_name'], loaded_monitors[ids]['id']
                monitor_info.append(to_add)
        else:
            print(f'Could not retrieve paused list. Error: \n{mydata}')
            exit()
        return monitor_info

## - Retrieves URL, friendlyName and ID for down monitors.

    def getDown(apikey, headers):
        monitor_info = []
        down = f'api_key={apikey}&format=json&statuses=9'
        conn.request("POST", "/v2/getMonitors/", down, headers)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        catchRateError(data)
        mydata = json.loads(data)
        if mydata['stat'] == 'ok':
            print('Received down list.')
            loaded_monitors = mydata['monitors']
            print(f'Number of monitors down: {len(loaded_monitors)}')
            for ids in range(len(loaded_monitors)):
                to_add = loaded_monitors[ids]['url'], loaded_monitors[ids]['friendly_name'], loaded_monitors[ids]['id']
                monitor_info.append(to_add)
        else:
            print(f'Could not retrieve down list. Error: \n{mydata}')
            exit()
        return monitor_info


## - Used to find rate limit errors. Common when using the free plan and the option to search all monitors.

pattern = re.compile(r'(Rate limit|Warning|Error)', re.IGNORECASE)

def catchRateError(data):
    try:
        if pattern.search(data):
            print(f'Error while executing API: \n{data}\nExiting.')
            exit()
    except BaseException as e:
        print(e)
        pass

## - Prints all account details as JSON.

def accountDetails(apikey, headers):
    get_account_details = f'api_key={apikey}&format=json'
    conn.request("POST", "/v2/getAccountDetails", get_account_details, headers)
    res = conn.getresponse()
    data = res.read()
    catchRateError(data)
    print('Getting account details as JSON file: ')         
    print(data.decode("utf-8"))

## - Retrieves contacts displaying name and ID.

def alertContacts(apikey, headers):
    get_alert_contacts = f'api_key={apikey}&format=json'
    conn.request("POST", "/v2/getAlertContacts", get_alert_contacts, headers)
    res = conn.getresponse()
    data = res.read()
    catchRateError(data)         
    mydata = json.loads(data)
    if mydata['stat'] == 'ok':
        print('Retriving contacts:')
        for ids in mydata['alert_contacts']:
            print(f'ID: {mydata["alert_contacts"][0]["id"]}, Name: {mydata["alert_contacts"][0]["friendly_name"]}')
    else:
        print('Could not list alertContacts')





