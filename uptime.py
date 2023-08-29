## - UptimeRobot API
## - Documentation → https://uptimerobot.com/api/
## - https://github.com/cvzero89/uptime-robot

import json
import http.client
import time
import re
import os
from dotenv import load_dotenv
import argparse
from datetime import datetime
apikey = None
script_path = os.path.abspath(os.path.dirname(__file__))
## - Loading the key from .env. If it does not exist it will ask to enter it manually.
env_path = f'{script_path}/.env'
def loadkey(env_path):
    try:
        load_dotenv(dotenv_path=env_path)
        load_key = os.environ['API_KEY']
        return load_key
    except KeyError:
        print('Could not load API key from .env file.')
    load_key = None
    while True:
        if load_key == None:
            load_key = input('API key is missing on the .env file. Enter it manually: ')
        break
    return load_key

## - Loading the contacts from .env. If it does not exist it will ask to enter it manually. 
## - It will assume contacts with recurrence _0_0.

def loadcontacts(env_path):
    try:
        load_dotenv(dotenv_path=env_path)
        contacts = os.environ['CONTACTS']
        contact_1 = []
        for contact in contacts.split('|'):
            contact_1.append(f'{contact}')
        alert_contacts = '-'.join(contact_1)
        return alert_contacts
    except KeyError:
        print('Missing CONTACTS from .env')
    contacts = None
    while True:
        if contacts == None:
            contacts = input('No contacts were found. Set your alert contacts based on their ID: ')
            contact_1 = []
            for contact in contacts.split('|'):
                contact_1.append(f'{contact}')
            alert_contacts = '-'.join(contact_1)
        break
    return alert_contacts

conn = http.client.HTTPSConnection("api.uptimerobot.com")

headers = {
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache"
    }

class Monitor:
    def __init__(self, domain, friendlyName='blank', monitorId=None, logs=None, type_='1', keyword=None, port=None, alert_contacts='blank', monitorInterval='300', monitorTimeout='60', monitorSSL='1'):
        self.type_ = type_
        self.domain = domain.replace('http://', '').replace('https://', '')
        self.friendlyName = friendlyName.replace(' ','')
        self.monitorInterval = monitorInterval
        self.monitorTimeout = monitorTimeout
        self.monitorSSL = monitorSSL
        self.monitorId = monitorId
        self.alert_contacts = alert_contacts.replace('{', '').replace('}', '')
        self.logs = logs
        self.keyword = keyword
        self.port = port


## - Edit domains. Needs to be feed a list in monitor_info and option_to_edit to be valid based on https://uptimerobot.com/api/.

    def editdomain(self, apikey, headers, option_to_edit):
        edit = f'api_key={apikey}&format=json&id={self.monitorId}&{option_to_edit}'
        conn.request("POST", "/v2/editMonitor", edit, headers)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        catchRateError(data)
        try:
            mydata = json.loads(data)
        except ValueError:
            print('Could not load JSON data.')
            exit()
        if mydata['stat'] == 'ok':
            print(f'Updated {self.friendlyName} successfully!')
        else:
            print(f'Update for {self.friendlyName} failed! Error: \n{mydata}')
            print('The option to edit must follow the API documentation at: https://uptimerobot.com/api/.')

## - Add domains. Needs the monitor and alert contacts to have been set.
    
    def addMonitor(self, apikey, headers):
        if self.keyword:
            keyword_type = self.keyword['keyword_type']
            keyword_case_type = self.keyword['keyword_case_type']
            keyword_value = self.keyword['keyword_value']
            adding = f'api_key={apikey}&format=json&type={self.type_}&url=https://{self.domain}&friendly_name={self.friendlyName}&keyword_type={keyword_type}&keyword_case_type={keyword_case_type}&keyword_value={keyword_value}&alert_contacts={self.alert_contacts}&timeout=60'
        elif self.port:
            port_sub_type = self.port['port_sub_type']
            port_number = self.port['port_number']
            adding = f'api_key={apikey}&format=json&type={self.type_}&url=https://{self.domain}&friendly_name={self.friendlyName}&sub_type={port_sub_type}&port={port_number}&alert_contacts={self.alert_contacts}&timeout=60'
        else:
            adding = f'api_key={apikey}&format=json&type={self.type_}&url=https://{self.domain}&friendly_name={self.friendlyName}&alert_contacts={self.alert_contacts}&timeout=60'
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

## - Delete monitors, used with searchMonitor.

    def deleteMonitor(self, apikey, headers):
        delete = f'api_key={apikey}&format=json&id={self.monitorId}'                 
        conn.request("POST", "/v2/deleteMonitor", delete, headers)            
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        catchRateError(data)
        try:
            mydata = json.loads(data)
        except ValueError:
            print('Could not load JSON data.')
            exit()
        if mydata['stat'] == 'ok':
            print(f'Monitor {self.friendlyName} deleted successfully!')
        else:
            print(f'Could not delete {self.friendlyName}. Error: \n{mydata}')

    def logParser(self):
        for log in self.logs[:5]:
            incident_id = log['id']
            time = datetime.fromtimestamp(log['datetime'])
            duration = log['duration'] / 60
            reason = log['reason']['detail']
            if log['type'] == 1:
                log_type = 'DOWN'
            elif log['type'] == 2:
                log_type = 'UP'
            elif log['type'] == 99:
                log_type = 'PAUSED'
            else:
                log_type = 'STARTED'
            print(f'Incident id: {incident_id}, type {log_type} at {time} for {round(duration, 2)} minutes. Reason: {reason}')
        print('\n')


def load_json(data):
    to_add = []
    monitor_info = []
    try:
        mydata = json.loads(data)
    except ValueError:
        print('Could not load JSON data.')
        exit()
    if mydata['stat'] == 'ok':
        loaded_monitors = mydata['monitors']
        number_of_monitors = len(loaded_monitors)
        for ids in range(number_of_monitors):
            try:
                to_add = loaded_monitors[ids]['url'], loaded_monitors[ids]['friendly_name'], loaded_monitors[ids]['id'], loaded_monitors[ids]['logs']
            except KeyError:
                to_add = loaded_monitors[ids]['url'], loaded_monitors[ids]['friendly_name'], loaded_monitors[ids]['id']
            monitor_info.append(to_add)
    else:
        print(f'Failed to retrieve monitor list \nError:')
        print(mydata)
    return number_of_monitors, monitor_info

## - Imports monitors from a CSV file, needs to be named uptimeimport.csv on the script directory. Executes addMonitor to add.

def add_in_batch(headers, apikey):
    import csv
    current_item = 1
    with open('uptimeimport.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            print(f'Current monitor: {row["URL/IP"]} - {current_item}')
            if row['Type'] == '2':
                keyword_dict = {}
                keyword_dict['keyword_type'] = row['Keyword Type']
                keyword_dict['keyword_case_type'] = row['Keyword Case Type']
                keyword_dict['keyword_value'] = row['Keyword Value']
                monitor = Monitor(row['URL/IP'], row['Friendly Name'], None, None, row['Type'], keyword_dict, None, row['Alert Contact'])
            elif row['Port'] != None:
                port_dict = {}
                if row['Port'] == '1':
                    port_dict['port_number'] = '80'
                    port_dict['port_sub_type'] = '1'
                elif row['Port'] == '2':
                    port_dict['port_number'] = '443'
                    port_dict['port_sub_type'] = '2'
                elif row['Port'] == '3':
                    port_dict['port_number'] = '21'
                    port_dict['port_sub_type'] = '3'
                elif row['Port'] == '4':
                    port_dict['port_number'] = '25'
                    port_dict['port_sub_type'] = '4'
                elif row['Port'] == '5':
                    port_dict['port_number'] = '110'
                    port_dict['port_sub_type'] = '5'
                elif row['Port'] == '6':
                    port_dict['port_number'] = '143'
                    port_dict['port_sub_type'] = '6'
                elif row['Port'] == '99':
                    port_dict['port_sub_type'] = '99'
                    port_dict['port_number'] = row['Custom port']
                monitor = Monitor(row['URL/IP'], row['Friendly Name'], None, None, row['Type'], None, port_dict, row['Alert Contact'])
            else:
                monitor = Monitor(row['URL/IP'], row['Friendly Name'], None, None, row['Type'], None, None, row['Alert Contact'])
            monitor.addMonitor(apikey, headers)
            current_item += 1
            sleepy()


## - Search monitors FriendlyName and URL. It can retrieve partial hits. Also used to retrieve ids for mass edits.

def searchMonitor(domain, apikey, headers, logs):
    if logs == True:
        logs_bool = '1'
    else:
        logs_bool = '0'
    monitor_info = []
    getinfomonitor = f'api_key={apikey}&format=json&search={domain}&logs={logs_bool}'
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
            try:
                to_add = loaded_monitors[ids]['url'], loaded_monitors[ids]['friendly_name'], loaded_monitors[ids]['id'], loaded_monitors[ids]['logs']
            except KeyError:
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

def getinfo(headers, apikey, logs): 
    offset_var_add = 0
    monitor_info = []
    try:
        offset = int(input('How many records do you want to display? (Min: 50): '))
        if offset <= 50:
            offset = 50
    except ValueError:
        offset = 100
        print('Invalid input, max. 150 records will be displayed.')
    if logs == True:
        logs_bool = '1'
    else:
        logs_bool = '0'
    for update_offset in range(0, offset,50):
        offset_var_full = f'offset={str(update_offset)}'
        getinfomonitor = f'api_key={apikey}&format=json&logs={logs_bool}&{offset_var_full}'
        conn.request("POST", "/v2/getMonitors", getinfomonitor, headers)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        catchRateError(data)
        number_of_monitors, monitor_info_temp = load_json(data)
        monitor_info = monitor_info + monitor_info_temp        
    return monitor_info

## - Retrieves URL, friendlyName and ID for paused monitors.

def getPaused(apikey, headers, logs):
    if logs == True:
        logs_bool = '1'
    else:
        logs_bool = '0'
    monitor_info = []
    paused = f'api_key={apikey}&format=json&statuses=0&logs={logs_bool}'
    conn.request("POST", "/v2/getMonitors/", paused, headers)
    res = conn.getresponse()
    data = res.read().decode('utf-8')
    catchRateError(data)
    number_of_monitors, monitor_info = load_json(data)
    print(f'Number of monitors paused: {number_of_monitors}')
    return monitor_info

## - Retrieves URL, friendlyName and ID for down monitors.

def getDown(apikey, headers, logs):
    if logs == True:
        logs_bool = '1'
    else:
        logs_bool = '0'
    monitor_info = []
    down = f'api_key={apikey}&format=json&statuses=9&logs={logs_bool}'
    conn.request("POST", "/v2/getMonitors/", down, headers)
    res = conn.getresponse()
    data = res.read().decode('utf-8')
    catchRateError(data)
    number_of_monitors, monitor_info = load_json(data)
    print(f'Number of monitors down: {number_of_monitors}')
    return monitor_info

## - Format to print information from the other functions.

def printInfo(monitor_info):
    print(f'Displaying {len(monitor_info)} records.')
    for info in monitor_info:
        monitor = Monitor(*info)
        print(f'\nDomain name: {monitor.domain}\nFriendly Name: {monitor.friendlyName}\nID: {monitor.monitorId}')
        if monitor.logs:
            monitor.logParser()

## - Used to find rate limit errors. Common when using the free plan and the option to search all monitors.

pattern = re.compile(r'(Rate limit|Warning)', re.IGNORECASE)

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
    data = res.read().decode('utf-8')
    catchRateError(data)
    try:
        mydata = json.loads(data)
    except ValueError:
        print('Could not load JSON data.')
        exit()
    if mydata['stat'] == 'ok':
        account = mydata["account"]
        try:
            print(f"""
Email: {account["email"]}
UserID: {account["user_id"]}
Subscription: {account["subscription_expiry_date"]}. Active? {account["active_subscription"]}. Registered: {account["registered_at"]}.
Monitor info: UP: {account["up_monitors"]}, DOWN: {account["down_monitors"]}, PAUSED: {account["paused_monitors"]}
Monitor Limit/Total added: {account["monitor_limit"]}/{account["total_monitors_count"]}
""")
        except KeyError as account_error:
            print(f'Error loading account JSON:\n{account_error}')

## - Retrieves contacts displaying name and ID.

def alertContacts(apikey, headers):
    get_alert_contacts = f'api_key={apikey}&format=json'
    conn.request("POST", "/v2/getAlertContacts", get_alert_contacts, headers)
    res = conn.getresponse()
    data = res.read().decode('utf-8')
    catchRateError(data)         
    mydata = json.loads(data)
    if mydata['stat'] == 'ok':
        print(f'Retriving contacts: {len(mydata["alert_contacts"])}')
        for ids in range(len(mydata['alert_contacts'])):
            print(f'ID: {mydata["alert_contacts"][ids]["id"]}, Name: {mydata["alert_contacts"][ids]["friendly_name"]}, Email: {mydata["alert_contacts"][ids]["value"]}')
    else:
        print('Could not list alertContacts')

def sleepy():
    time.sleep(2)

def main():
    parser =  argparse.ArgumentParser(description='UptimeRobot API CLI.', add_help=False)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='More info on GitHub: https://github.com/cvzero89/uptime-robot')
    parser.add_argument('action', type = str.lower, choices=['account_info', 'show_alert_contacts', 'monitor_search', 'show_all_monitors', 'add_manually', 'add_in_batch', 'delete_monitor', 'edit_monitor', 'get_paused_monitors', 'get_down_monitors'], help='Enter the action to perform on UptimeRobot.')
    parser.add_argument('--logs', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    logs = args.logs
    apikey = loadkey(env_path)

    if args.action == 'account_info':
        accountDetails(apikey, headers)

    if args.action == 'show_alert_contacts':
        alertContacts(apikey, headers)

    if args.action == 'show_all_monitors':
        if logs == None:
            logs == False
        monitor_info = getinfo(headers, apikey, logs)
        printInfo(monitor_info)

    if args.action == 'monitor_search':
        domain = input('Type the domain to search: ')
        if logs == None:
            logs == False
        monitor_info = searchMonitor(domain, apikey, headers, logs)
        printInfo(monitor_info)

    if args.action == 'get_down_monitors':
        monitor_info = getDown(apikey, headers, logs)
        printInfo(monitor_info)

    if args.action == 'get_paused_monitors':
        monitor_info = getPaused(apikey, headers, logs)
        printInfo(monitor_info)

    if args.action == 'delete_monitor':
        domain = input('Type the domain to delete: ')
        if logs == None:
            logs == False
        monitor_info = searchMonitor(domain, apikey, headers, logs)
        printInfo(monitor_info)
        confirm_edit = input('These domains will be deleted. Confirm [Y/N]: ')
        if confirm_edit.lower() == 'y':
            for info in monitor_info:
                monitor = Monitor(*info)
                monitor.deleteMonitor(apikey, headers)
                sleepy()
        else:
            exit()

    if args.action == 'edit_monitor':
        question = input('Edit all monitors or filter monitors? (All/Filter): ')
        if question.lower() == 'all':
            option_to_edit = input('What do you want to edit?: ')
            logs = False
            monitor_info = getinfo(headers, apikey, logs)
            for info in monitor_info:
                monitor = Monitor(*info)
                monitor.editdomain(apikey, headers, option_to_edit)
                sleepy()
        elif question.lower() == 'filter':
            domain = input('Type the domain to search: ')
            if logs == None:
                logs == False
            monitor_info = searchMonitor(domain, apikey, headers, logs)
            printInfo(monitor_info)
            confirm_edit = input('These domains will be edited. Confirm [Y/N]: ')
            if confirm_edit.lower() == 'y':
                option_to_edit = input('What do you want to edit?: ')
                for info in monitor_info:
                    monitor = Monitor(*info)
                    monitor.editdomain(apikey, headers, option_to_edit)
                    sleepy()
            else:
                exit()
        else:
            print('Invalid option.')
            exit()




    if args.action == 'add_manually':
        alert_contacts = loadcontacts(env_path)
        question = int(input("How many domains will you add?: "))

        for number in range(question):
            domain = input("Domain: ") 
            friendly_name = input("friendlyName: ")
            monitor_id = None 
            monitor_log = None 
            monitor_type = input("""Type? 
        1 - HTTP(s)
        2 - Keyword
        3 - Ping
        4 - Port
        5 - Heartbeat\nEnter one of the options above: """)
            if monitor_type == '2':
                keyword_dict = {}
                keyword_dict['keyword_type'] = input("1 - Exists or 2 - Does not exist: ")
                keyword_dict['keyword_case_type'] = input("0 - Case sensitive or 1 - Case insensitive: ")
                keyword_dict['keyword_value'] = input("Enter your keyword: ")
                monitor = Monitor(domain, friendly_name, None, None, monitor_type, keyword_dict, None, alert_contacts)
            elif monitor_type == '4':
                port_dict = {}
                port_dict['port_sub_type'] = input("""Port type:
        1 - HTTP (80)
        2 - HTTPS (443)
        3 - FTP (21)
        4 - SMTP (25)
        5 - POP3 (110)
        6 - IMAP (143)
        99 - Enter Custom Port\nEnter one of the options above: """)
                if port_dict['port_sub_type'] == '1':
                    port_dict['port_number'] = '80'
                elif port_dict['port_sub_type'] == '2':
                    port_dict['port_number'] = '443'
                elif port_dict['port_sub_type'] == '3':
                    port_dict['port_number'] = '21'
                elif port_dict['port_sub_type'] == '4':
                    port_dict['port_number'] = '25'
                elif port_dict['port_sub_type'] == '5':
                    port_dict['port_number'] = '110'
                elif port_dict['port_sub_type'] == '6':
                    port_dict['port_number'] = '143'
                elif port_dict['port_sub_type'] == '99':
                    port_dict['port_number'] = input('Enter custom port: ')
                monitor = Monitor(domain, friendly_name, None, None, monitor_type, None, port_dict, alert_contacts)
            else:
                monitor = Monitor(domain, friendly_name, None, None, monitor_type, None, None, alert_contacts)
            monitor.addMonitor(apikey, headers)

    if args.action == 'add_in_batch':
        print('File assumed as uptimerobot.csv on the script directory.')
        add_in_batch(headers, apikey)


if __name__ == "__main__":
    main()
