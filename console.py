#!/usr/bin/env python3

import lib27gn950

import hid
# https://pypi.org/project/hid/
# https://github.com/apmorton/pyhidapi

import re
import sys



help_text = '''\
Valid commands:

  exit   quit   q
    Exit

  help   h   ?
    Show this message

  info
    Show info about connected monitors

  select
    Select which monitors to control
    Examples:
      select 2        (control just the 2nd monitor)
      select 1 2 5    (control these three monitors)
      select all      (this is the default setting when the program starts)
      select          (this is the same as doing "select all")

  turn_on   turn_off
    Turn the lighting on or off

  color1   color2   color3   color4
    Set the lighting to one of the four static color options

  color_peaceful   color_dynamic
    Set the lighting mode to one of the non-static color options

  1   2   3   4   5   6   7   8   9   10   11   12
    Set the lighting brightness. 1 is minumum, 12 is maximum.

  set
    Set the color saved in one of the static color slots
    Arguments: slot number, color
    The color argument must be provided as a 6 character (3 byte RGB) hex string
    Command example:
      set 2 ff2b83

  <128 character hex string>
    Send a raw command, entered as a 128-char hex string (representing 64 bytes)

  Video sync is not supported in console mode
'''


devs = []
selected = []


def setup():
	global selected
	monitors = lib27gn950.find_monitors()
	if not monitors:
		print('No monitors found')
		sys.exit(0)
	for monitor in monitors:
		devs.append(hid.Device(path=monitor['path']))
	selected = list(range(len(devs)))


def cleanup():
	for dev in devs:
		dev.close()


def get_selected_devs():
	result = []
	for x in selected:
		result.append(devs[x])
	return result

	
def cli():
	while True:
		try:
			text = input(': ').lower().strip()
			cli_process_line(text)
		except KeyboardInterrupt as e:
			print()
			sys.exit(0)
		except EOFError as e:
			sys.exit(0)


def noninteractive():
	global selected

	cmd = ' '.join([x.lower() for x in sys.argv[1:]]).strip()
	selection = []

	try:
		if ',' in cmd:
			parts = [x for x in cmd.split(',') if (x != '' and not x.isspace())]
			cmd = parts[-1]
			selection = parts[:-1]
		if selection and not ('all' in selection): # default selection is all
			selected = [int(num)-1 for num in selection]
			selected = [x for x in selected if x >= 0 and x < len(devs)]
	except:
		print('Error parsing command', file=sys.stderr)
		sys.exit(1)

	if not selected:
		print('The provided selection selects nothing')
		sys.exit(0)

	cli_process_line(cmd)


def cli_process_line(text):
	global selected

	if text in ['exit', 'quit', 'q']:
		sys.exit(0)

	elif text in ['help', 'h', '?']:
		print(help_text)

	elif text in lib27gn950.control_commands.keys():
		lib27gn950.send_command(lib27gn950.control_commands[text], get_selected_devs())

	elif text in [str(x) for x in range(1, 13)]:
		lib27gn950.send_command(lib27gn950.brightness_commands[int(text)], get_selected_devs())

	elif len(text) == 128:
		lib27gn950.send_raw_command(text, get_selected_devs())

	elif text == 'select' or re.match(r'select +all', text):
		selected = list(range(len(devs)))
		cli_process_line('info')

	elif re.match(r'^select( +\d+)+$', text):
		selected = [int(num)-1 for num in text.split()[1:]]
		selected = [x for x in selected if x >= 0 and x < len(devs)]
		cli_process_line('info')

	elif re.match(r'^set [1-4] [0-9a-f]{6}$', text):
		parts = text.split()
		slot = int(parts[1])
		color = parts[2]
		lib27gn950.send_command(lib27gn950.get_set_color_command(slot, color), get_selected_devs())

	elif text in ['info']:
		if not devs:
			print('No monitors connected')
		else:
			print(f'Connected to {len(devs)} monitor' + ('' if len(devs) == 1 else 's'))
			print(f'Monitors marked with * are currently selected')
			print()
			for i in range(len(devs)):
				print(f'{"*" if i in selected else " "} {i+1}: serial number {devs[i].serial}')
		print()

	else:
		print('Command not recognized. Enter "help" for help.')
		print()


if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'h', 'help', '?']:
		print(help_text)
		sys.exit(0)
	try:
		setup()
		if len(sys.argv) > 1:
			noninteractive()
		else:
			print(f'Connected to {len(devs)} monitors')
			cli()
	finally:
		cleanup()
