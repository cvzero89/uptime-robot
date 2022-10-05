from uptime import *
import argparse

parser =  argparse.ArgumentParser(description='UptimeRobot API CLI.', add_help=False)
parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='More info on GitHub: https://github.com/cvzero89/uptime-robot')
parser.add_argument('action', type = str.lower, choices=['account_info', 'show_alert_contacts', 'monitor_search', 'show_all_monitors', 'add_single', 'add_in_batch', 'delete_monitor', 'edit_monitor', 'get_paused_monitors', 'get_down_monitors'], help='Enter the action to perform on UptimeRobot.')
args = parser.parse_args()

apikey = loadkey()

if args.action == 'account_info':
	accountDetails(apikey, headers)
	exit()

if args.action == 'show_alert_contacts':
	alertContacts(apikey, headers)
	exit()

if args.action == 'show_all_monitors':
	monitor_info = Monitor.getinfo(headers, apikey)
	Monitor.printInfo(monitor_info)
	exit()

if args.action == 'monitor_search':
	monitor = input('Type the domain to search: ')
	monitor_info = Monitor(monitor).searchMonitor(apikey, headers)
	Monitor.printInfo(monitor_info)
	exit() 

if args.action == 'get_down_monitors':
	monitor_info = Monitor.getDown(apikey, headers)
	Monitor.printInfo(monitor_info)

if args.action == 'get_paused_monitors':
	monitor_info = Monitor.getPaused(apikey, headers)
	Monitor.printInfo(monitor_info)

if args.action == 'delete_monitor':
	monitor = input('Type the domain to delete: ')
	monitor_info = Monitor(monitor).searchMonitor(apikey, headers)
	delete_monitor = Monitor.deleteMonitor(monitor_info, apikey, headers)

if args.action == 'edit_monitor':
	question = input('Edit all monitors or filter monitors? (All/Filter): ')
	if question.lower() == 'all':
		option_to_edit = input('What do you want to edit?: ')
		monitor_info = Monitor.getinfo(headers, apikey)
		Monitor.editdomain(monitor_info, apikey, headers, option_to_edit)
	elif question.lower() == 'filter':
		monitor = input('Type the domain to search: ')
		monitor_info = Monitor(monitor).searchMonitor(apikey, headers)
		Monitor.printInfo(monitor_info)
		confirm_edit = input('These domains will be edited. Confirm [Y/N]: ')
		if confirm_edit.lower() == 'y':
			option_to_edit = input('What do you want to edit?: ')
			Monitor.editdomain(monitor_info, apikey, headers, option_to_edit)
		else:
			exit()
	else:
		print('Invalid option.')
		exit()


alert_contacts = loadcontacts()

if args.action == 'add_single':
	question = int(input("How many domains will you add?: "))

	for number in range(question):
		monitor = Monitor(input("Domain: "), input("friendlyName: "), None, input("""Type? 
	1 - HTTP(s)
	2 - Keyword
	3 - Ping
	4 - Port
	5 - Heartbeat\n(Only HTTP(s) Supported at the time): """))
		monitor.add_single(apikey, headers, alert_contacts)

if args.action == 'add_in_batch':
	print('File assumed as uptimerobot.csv on the script directory.')
	add_in_batch(headers, apikey)





