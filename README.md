# UptimeRobot CLI
CLI based on UptimeRobot API: https://uptimerobot.com/api/

## Usage

```
$ python3 uptime-cli.py 
usage: uptime-cli.py [-h]
                     {account_info,show_alert_contacts,monitor_search,show_all_monitors,add_single,add_in_batch,delete_monitor,edit_monitor,get_paused_monitors,get_down_monitors}
uptime-cli.py: error: the following arguments are required: action 
```

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

Adding domains:
```
$ python3 uptime-cli.py add_single
How many domains will you add?: 1
Domain: test-example.com
friendlyName: test
Type?
	1 - HTTP(s)
	2 - Keyword
	3 - Ping
	4 - Port
	5 - Heartbeat
(Only HTTP(s) Supported at the time): 1
Added test successfully!
```

Searching monitors based on strings on the friendlyName or URL:

```
$ python3 uptime-cli.py monitor_search
Type the domain to search: .com
Displaying 9 records.

Domain name: anothersite.com
Friendly Name: anothersite.com
ID: 792797966
```

The APIKEY and contacts can be set on a .env file, format;
```
API_KEY=
CONTACTS=
```

If multiple contacts they need to be separated with |

```
CONTACTS=2342342|353453
```
Contacts are assumed as having recurrence/threshold _0_0.
