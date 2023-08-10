# UptimeRobot CLI
CLI based on UptimeRobot API: https://uptimerobot.com/api/

## Usage

```
$ python3 uptime.py
usage: uptime.py [-h] [--logs | --no-logs]
                 {account_info,show_alert_contacts,monitor_search,show_all_monitors,add_manually,add_in_batch,delete_monitor,edit_monitor,get_paused_monitors,get_down_monitors}
```

(Some actions might hit API limits depending on the plan)

### Examples:

Listing all monitors will need multiple queries to the API since they only allow to return 50 monitors at a time.

```
$ python3 uptime-cli.py show_all_monitors
How many records do you want to display?: 100
Displaying 9 records.

Domain name: anothersite.com
Friendly Name: anothersite.com
ID: 792797966

Domain name: hello.com
Friendly Name: hello.com
ID: 792797865
```

#### Adding domains:
```
$ python3 uptime.py add_manually
How many domains will you add?: 1
Domain: test.com
friendlyName: test
Type?
        1 - HTTP(s)
        2 - Keyword
        3 - Ping
        4 - Port
        5 - Heartbeat
Enter one of the options above: 1
Added test successfully!
```
To add in batch the importcsv file needs to be filled. Not all columns are required, "Friendly Name", "URL/IP", "Alert Contacts" are the only ones taken into account.

#### Listing monitors with logs:

```
$ python3 uptime.py show_all_monitors --logs
Domain name: domain.com
Friendly Name: domain.com
ID: 794988524
Incident id: 3109569097, type UP at 2023-08-10 13:32:56 for 100.42 minutes. Reason: OK
Incident id: 3109568876, type STARTED at 2023-08-10 13:32:19 for 0.62 minutes. Reason: Monitor started
``` 

#### Searching monitors based on strings on the friendlyName or URL:

```
$ python3 uptime-cli.py monitor_search
Type the domain to search: .com
Displaying 9 records.

Domain name: anothersite.com
Friendly Name: anothersite.com
ID: 792797966
```

#### Deleting domains based on search:
```
$ python3 uptime.py delete_monitor
Type the domain to delete: .com
Displaying 2 records.

Domain name: example.com
Friendly Name: example.com
ID: 794972680

Domain name: domain.com
Friendly Name: domain.com
ID: 794988524

These domains will be deleted. Confirm [Y/N]: y
Monitor example.com deleted successfully!
Monitor domain.com deleted successfully!
```

#### The APIKEY and contacts can be set on a .env file, format;
```
API_KEY=
CONTACTS=
```

If multiple contacts they need to be separated with |. _0_0 is the threshold_recurrence, needs to be set according to https://uptimerobot.com/api/.

```
CONTACTS=2342342_0_0|353453_0_0
```

#### Account info:
```
$ python3 uptime.py account_info

Email: carlos@example.com
UserID: 12345
Subscription: None. Active? None. Registered: 2022-09-19T11:55:14.000Z.
Monitor info: UP: 1, DOWN: 0, PAUSED: 0
Monitor Limit/Total added: 50/1
```
