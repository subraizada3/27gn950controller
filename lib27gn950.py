#!/usr/bin/env python3

import hid
# https://pypi.org/project/hid/
# https://github.com/apmorton/pyhidapi

# Library API documentation:
#
# Note: A small example program is located at the bottom of this file
#
#
# find_monitors()
#   Searches through HID devices and returns a list of dictionaries of the form:
#     { 'path': hid_device_path,
#       'serial': '010NTNHNL976' }
#   You can open a HID device like so:
#     monitors = find_monitors()
#     with hid.Device(path=monitors[0]['path']) as monitor0_dev:
#       ... do stuff ...
#       side note: `monitor0_dev.serial` is a string containing the serial number
#
#
# send_command(cmd, dev)
#   Given a command(s), send it to the device
#   `dev` must be an open hid.Device instance, or an iterable of them
#   `cmd` must be either an 11-character hex string, or an iterable of
#     11-character hex strings. Providing an iterable is equivalent to sending
#     multiple commands consecutively. For example, these two are equivalent:
#
#       cmd1 = '11-character hex string'
#       cmd2 = '11-character hex string'
#       cmds = (cmd1, cmd2)
#
#       Option A:
#       send_command(cmd1, dev)
#       send_command(cmd2, dev)
#
#       Option B:
#       send_command(cmds, dev)
#
#
# send_raw_command(cmd, dev)
#   Send a command to the device
#   `dev` must be an open hid.Device instance, or an iterable of them
#   `cmd` must be a 128-character hex string (representing 64 bytes)
#
#
#
# control_commands
#   This is a dictionary of commands. Pass the values to send_command. Example:
#     monitors = find_monitors()
#     with hid.Device(path=monitors[0]['path']) as monitor0_dev:
#       send_command(control_commands['turn_on'], monitor0_dev)
#   Available commands (keys) are:
#     turn_on   turn_off
#     color1   color2   color3   color4
#     color_peaceful   color_dynamic   color_video_sync
#   The is the same set of actions that you can do using the scroll wheel
#     on the bottom of the monitor.
#
#
# brightness_commands
#   This is a dictionary of commands. Pass the values to send_command.
#   The keys are the integers [1..12]. Example:
#     send_command(brightness_commands[ 1], dev) # set to min brightness
#     send_command(brightness_commands[ 6], dev) # set to a moderate brightness
#     send_command(brightness_commands[12], dev) # set to max brightness
#
#
# get_set_color_command(slot, color)
#   Get the command to set the color for a static color slot
#   `slot` must be an integer in the range [1..4]
#   `color` must be a valid color string (described below)
#   Example:
#     Set static color slot 2 to a bluish red, with a bit of green mixed in
#     send_command(get_set_color_command(2, 'ff20e0', dev))
#
#
#
# send_video_sync_data(colors, dev)
#   Send a video sync data frame
#   `colors` must be a list of 48 color strings
#
#
#
# Color strings:
#   The monitor acceps colors in the  8-bit RGB format (the usual (0,0,0) to
#     (255,255,255). However, only a limited subset of colors are usable, it
#     doesn't have a full 8 bits of values per channel. Instead, each channel
#     must be one of 8 values:
#
#   Decimal:  0, 32, 64, 128, 160, 192, 224, 255
#   Hex:     00, 20, 40,  80,  a0,  c0,  e0,  ff
#
#   Colors must be provided as a lowercase RGB hex string.
#
#   Additionally, the colors are further limited. One channel must always be
#     0xff. And with the sole exception of white (ffffff), it is invalid to make
#     all three channels nonzero. In other words, all valid colors except white
#     conform to this format:
#       One channel is 0xff
#       Another channel is anything
#       The third channel is 0x00
#
#   Examples:
#     ff0000: valid: one channel is 0xff, one is 0x00, one is anything
#     00ffff: valid: one channel is 0xff, one is 0x00, one is anything
#     e000ff: valid: one channel is 0xff, one is 0x00, one is anything
#     e000e0: invalid: no channel is 0xff
#     e020ff: invalid: cannot have nonzero values in all three channels
#     ffffff: valid: white is the only exception to the above rule
#
#   `valid_colors` is a list of all the 44 valid color strings.

################################################################################


control_commands = {
	'turn_on':          'f02020100de',
	'turn_off':         'f02020200dd',
	'color1':           'a02020301d8',
	'color2':           'a02020302db',
	'color3':           'a02020303da',
	'color4':           'a02020304dd',
	'color_peaceful':   'a02020305dc',
	'color_dynamic':    'a02020306df',
	'color_video_sync': 'a02020308d1',
}

brightness_commands = {
	 1: 'f02020101df',
	 2: 'f02020102dc',
	 3: 'f02020103dd',
	 4: 'f02020104da',
	 5: 'f02020105db',
	 6: 'f02020106d8',
	 7: 'f02020107d9',
	 8: 'f02020108d6',
	 9: 'f02020109d7',
	10: 'f0202010ad4',
	11: 'f0202010bd5',
	12: 'f0202010cd2',
}


################################################################################

def get_set_color_command(slot, color):
	if slot not in [1,2,3,4]:
		raise ValueError('get_set_color_command: slot must be an integer in the range [1..4]')
	if color not in valid_colors:
		raise ValueError('get_set_color_command: invalid color')
	checksum = color_checksums[(slot, color)]
	colorstr = f'0{slot}{color}{checksum}'
	return 'd0204' + colorstr

################################################################################
################################################################################


def find_monitors():
	device_paths = []
	for device in hid.enumerate():
		vid = device['vendor_id']
		pid = device['product_id']
		usage_page = device['usage_page']
		if vid == 0x043e and pid == 0x9a8a and usage_page == 0xff01:
			device_paths.append({
				'path': device['path'],
				'serial': device['serial_number']
			})
	return device_paths

################################################################################

def send_raw_command(cmd, dev):
	if not hasattr(dev, '__iter__'):
		dev = (dev,)
	for _dev in dev:
		send_str(cmd, _dev)

################################################################################

def send_command(cmd, dev):
	header = '5343c'
	end = '4544'
	if type(cmd) == str:
		cmd = (cmd,)
	if not hasattr(dev, '__iter__'):
		dev = (dev,)
	for _dev in dev:
		for _cmd in cmd:
			padding = '0'*(119-len(_cmd)) # 128 chars - '5343c' - '4544' = 119
			send_str(header + _cmd + end + padding, _dev)

################################################################################

def send_video_sync_data(colors, dev):
	if len(colors) != 48:
		raise ValueError('send_video_sync_data: must provide 48 colors')
	for color in colors:
		if color not in valid_colors:
			raise ValueError('send_video_sync_data: invalid color')

	# generate the full command
	cmd = '5343c1029100'
	cmd += ''.join(colors)
	cmd += 'ff4544' # TODO: calculate checksum instead of using ff

	# split into three 64 byte (128 char) commands
	cmd1 = cmd[:128]
	cmd2 = cmd[128:256]
	cmd3 = cmd[256:] + '0'*78 # pad with zeroes to get to 64 bytes / 128 chars

	send_raw_command(cmd1, dev)
	send_raw_command(cmd2, dev)
	send_raw_command(cmd3, dev)


################################################################################
################################################################################


def send_str(s, dev):
	# s should be a 128-character hex string (representing 64 bytes)
	i = int(s, 16)
	dev.write(i.to_bytes(64, byteorder='big'))


################################################################################
################################################################################

valid_colors = [
	# reds, part 1
	'ff0000', 'ff0020', 'ff0040', 'ff0080', 'ff00a0', 'ff00c0', 'ff00e0',
	'ff00ff', # red-blue
	# blues
	'e000ff', 'c000ff', 'a000ff', '8000ff', '4000ff', '2000ff', '0000ff', '0020ff', '0040ff', '0080ff', '00a0ff', '00c0ff', '00e0ff',
	'00ffff', # blue-green
	# greens
	'00ffe0', '00ffc0', '00ffa0', '00ff80', '00ff40', '00ff20', '00ff00', '20ff00', '40ff00', '80ff00', 'a0ff00', 'c0ff00', 'e0ff00',
	'ffff00', # red-green
	# reds, part 2
	'ffe000', 'ffc000', 'ffa000', 'ff8000', 'ff4000', 'ff2000', 'ff0000',
	# white
	'ffffff'
]

color_checksums = {
	(1, 'ff0000'): '25',
	(1, 'ff0020'): '05',
	(1, 'ff0040'): '65',
	(1, 'ff0080'): 'a5',
	(1, 'ff00a0'): '85',
	(1, 'ff00c0'): 'e5',
	(1, 'ff00e0'): 'c5',
	(1, 'ff00ff'): 'da',
	(1, 'e000ff'): 'c5',
	(1, 'c000ff'): 'e5',
	(1, 'a000ff'): '85',
	(1, '8000ff'): 'a5',
	(1, '4000ff'): '65',
	(1, '2000ff'): '05',
	(1, '0000ff'): '25',
	(1, '0020ff'): '05',
	(1, '0040ff'): '65',
	(1, '0080ff'): 'a5',
	(1, '00a0ff'): '85',
	(1, '00c0ff'): 'e5',
	(1, '00e0ff'): 'c5',
	(1, '00ffff'): 'da',
	(1, '00ffe0'): 'c5',
	(1, '00ffc0'): 'e5',
	(1, '00ffa0'): '85',
	(1, '00ff80'): 'a5',
	(1, '00ff40'): '65',
	(1, '00ff20'): '05',
	(1, '00ff00'): '25',
	(1, '20ff00'): '05',
	(1, '40ff00'): '65',
	(1, '80ff00'): 'a5',
	(1, 'a0ff00'): '85',
	(1, 'c0ff00'): 'e5',
	(1, 'e0ff00'): 'c5',
	(1, 'ffff00'): 'da',
	(1, 'ffe000'): 'c5',
	(1, 'ffc000'): 'e5',
	(1, 'ffa000'): '85',
	(1, 'ff8000'): 'a5',
	(1, 'ff4000'): '65',
	(1, 'ff2000'): '05',
	(1, 'ff0000'): '25',
	(1, 'ffffff'): '25',
	(2, 'ff0000'): '26',
	(2, 'ff0020'): '06',
	(2, 'ff0040'): '66',
	(2, 'ff0080'): 'a6',
	(2, 'ff00a0'): '86',
	(2, 'ff00c0'): 'e6',
	(2, 'ff00e0'): 'c6',
	(2, 'ff00ff'): 'd9',
	(2, 'e000ff'): 'c6',
	(2, 'c000ff'): 'e6',
	(2, 'a000ff'): '86',
	(2, '8000ff'): 'a6',
	(2, '4000ff'): '66',
	(2, '2000ff'): '06',
	(2, '0000ff'): '26',
	(2, '0020ff'): '06',
	(2, '0040ff'): '66',
	(2, '0080ff'): 'a6',
	(2, '00a0ff'): '86',
	(2, '00c0ff'): 'e6',
	(2, '00e0ff'): 'c6',
	(2, '00ffff'): 'd9',
	(2, '00ffe0'): 'c6',
	(2, '00ffc0'): 'e6',
	(2, '00ffa0'): '86',
	(2, '00ff80'): 'a6',
	(2, '00ff40'): '66',
	(2, '00ff20'): '06',
	(2, '00ff00'): '26',
	(2, '20ff00'): '06',
	(2, '40ff00'): '66',
	(2, '80ff00'): 'a6',
	(2, 'a0ff00'): '86',
	(2, 'c0ff00'): 'e6',
	(2, 'e0ff00'): 'c6',
	(2, 'ffff00'): 'd9',
	(2, 'ffe000'): 'c6',
	(2, 'ffc000'): 'e6',
	(2, 'ffa000'): '86',
	(2, 'ff8000'): 'a6',
	(2, 'ff4000'): '66',
	(2, 'ff2000'): '06',
	(2, 'ff0000'): '26',
	(2, 'ffffff'): '26',
	(3, 'ff0000'): '27',
	(3, 'ff0020'): '07',
	(3, 'ff0040'): '67',
	(3, 'ff0080'): 'a7',
	(3, 'ff00a0'): '87',
	(3, 'ff00c0'): 'e7',
	(3, 'ff00e0'): 'c7',
	(3, 'ff00ff'): 'd8',
	(3, 'e000ff'): 'c7',
	(3, 'c000ff'): 'e7',
	(3, 'a000ff'): '87',
	(3, '8000ff'): 'a7',
	(3, '4000ff'): '67',
	(3, '2000ff'): '07',
	(3, '0000ff'): '27',
	(3, '0020ff'): '07',
	(3, '0040ff'): '67',
	(3, '0080ff'): 'a7',
	(3, '00a0ff'): '87',
	(3, '00c0ff'): 'e7',
	(3, '00e0ff'): 'c7',
	(3, '00ffff'): 'd8',
	(3, '00ffe0'): 'c7',
	(3, '00ffc0'): 'e7',
	(3, '00ffa0'): '87',
	(3, '00ff80'): 'a7',
	(3, '00ff40'): '67',
	(3, '00ff20'): '07',
	(3, '00ff00'): '27',
	(3, '20ff00'): '07',
	(3, '40ff00'): '67',
	(3, '80ff00'): 'a7',
	(3, 'a0ff00'): '87',
	(3, 'c0ff00'): 'e7',
	(3, 'e0ff00'): 'c7',
	(3, 'ffff00'): 'd8',
	(7, '000000'): '24',
	(3, 'ffe000'): 'c7',
	(3, 'ffc000'): 'e7',
	(3, 'ffa000'): '87',
	(3, 'ff8000'): 'a7',
	(3, 'ff4000'): '67',
	(3, 'ff2000'): '07',
	(3, 'ff0000'): '27',
	(3, 'ffffff'): '27',
	(4, 'ff0000'): '20',
	(4, 'ff0020'): '00',
	(4, 'ff0040'): '60',
	(4, 'ff0080'): 'a0',
	(4, 'ff00a0'): '80',
	(4, 'ff00c0'): 'e0',
	(4, 'ff00e0'): 'c0',
	(4, 'ff00ff'): 'df',
	(4, 'e000ff'): 'c0',
	(4, 'c000ff'): 'e0',
	(4, 'a000ff'): '80',
	(4, '8000ff'): 'a0',
	(4, '4000ff'): '60',
	(4, '2000ff'): '00',
	(4, '0000ff'): '20',
	(4, '0020ff'): '00',
	(4, '0040ff'): '60',
	(4, '0080ff'): 'a0',
	(4, '00a0ff'): '80',
	(4, '00c0ff'): 'e0',
	(4, '00e0ff'): 'c0',
	(4, '00ffff'): 'df',
	(4, '00ffe0'): 'c0',
	(4, '00ffc0'): 'e0',
	(4, '00ffa0'): '80',
	(4, '00ff80'): 'a0',
	(4, '00ff40'): '60',
	(4, '00ff20'): '00',
	(4, '00ff00'): '20',
	(4, '20ff00'): '00',
	(4, '40ff00'): '60',
	(4, '80ff00'): 'a0',
	(4, 'a0ff00'): '80',
	(4, 'c0ff00'): 'e0',
	(4, 'e0ff00'): 'c0',
	(4, 'ffff00'): 'df',
	(4, 'ffe000'): 'c0',
	(4, 'ffc000'): 'e0',
	(4, 'ffa000'): '80',
	(4, 'ff8000'): 'a0',
	(4, 'ff4000'): '60',
	(4, 'ff2000'): '00',
	(4, 'ff0000'): '20',
	(4, 'ffffff'): '20',
}

################################################################################
################################################################################

# Example usage

if __name__ == '__main__':
	import hid
	from sys import exit
	from time import sleep

	monitors = find_monitors()
	if not monitors:
		print('No monitors found')
		exit(0)

	print(f'Found {len(monitors)} monitor' + ('' if len(monitors) == 1 else 's'))

	devs = []
	for monitor in monitors:
		dev = hid.Device(path=monitor['path'])
		print(f'Got monitor with serial number {dev.serial}')
		devs.append(dev)

	print('Starting demonstration')
	print('Switching to static color slot 1')
	send_command(control_commands['color1'], devs)
	print('Setting brightness to 12 (maximum)')
	send_command(brightness_commands[12], devs)
	sleep(2)
	print('Setting slot 1 color to red with a bit of blue')
	send_command(get_set_color_command(1, 'ff0020'), devs)
	sleep(2)
	print('Setting slot 1 color to greenish blue')
	send_command(get_set_color_command(1, '00e0ff'), devs)
	sleep(2)
	print('Switching to static color slot 2')
	send_command(control_commands['color2'], devs)
	print('Setting brightness to 5')
	send_command(brightness_commands[5], devs)
	sleep(3)
	print('Setting brightness to 12')
	send_command(brightness_commands[12], devs)
	print('Switching to dynamic color mode')
	send_command(control_commands['color_dynamic'], devs)
	sleep(4)
	print('Switching to peaceful color mode')
	send_command(control_commands['color_peaceful'], devs)
	sleep(6)
	print('Turning off lighting')
	send_command(control_commands['turn_off'], devs)
	sleep(2)
	print('Turning lighting on to static color slot 1 with brightness 9')
	# The monitor doesn't require an explicit turn_on command. However, doing
	#   turn_on will maintain the previous (pre-turn_off) color mode/state,
	#   whereas this will always set it to the 1st static color.
	send_command(control_commands['color1'], devs)
	send_command(brightness_commands[9], devs)
	print('All done, exiting')

	for dev in devs:
		dev.close()
