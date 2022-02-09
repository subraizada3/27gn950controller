#!/usr/bin/env python3

import os, platform, ctypes
if 'Windows' in platform.system():
	ctypes.windll.LoadLibrary(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'hidapi.dll')

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
#       'serial': '010NTNHNL976',
#       'model': '38GL950G' }
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
#   `color` must be a color string (described below)
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
#     (255,255,255). Colors must be provided as a lowercase RGB hex string,
#     such as 'ffffff' or 'a0e27b'.

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

	cmd_data = f'0{slot}{color}'
	cmd = 'd0204' + cmd_data
	cmd_with_header = '5343c' + cmd

	return cmd + calc_crc(cmd_with_header)

################################################################################
################################################################################


vids_pids = {
	(0x043e, 0x9a8a): '27GN950 / 38GN950',
	(0x043e, 0x9a57): '38GL950G',
}
def find_monitors():
	device_paths = []
	for device in hid.enumerate():
		vid = device['vendor_id']
		pid = device['product_id']
		usage_page = device['usage_page']
		if (vid, pid) in vids_pids.keys() and usage_page == 0xff01:
			device_paths.append({
				'path': device['path'],
				'serial': device['serial_number'],
				'model': vids_pids[(vid, pid)],
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

	# each RGB component must be at least 1, otherwise the monitor can 'crash'
	newcolors = []
	for color in colors:
		newcolor = ''
		if color[0]==color[1]=='0': newcolor += '01'
		else: newcolor += color[0:2]
		if color[2]==color[3]=='0': newcolor += '01'
		else: newcolor += color[2:4]
		if color[4]==color[5]=='0': newcolor += '01'
		else: newcolor += color[4:6]
		newcolors.append(newcolor)

	# generate the full command
	cmd = '5343c1029100'
	cmd += ''.join(newcolors)
	cmd += calc_crc(cmd)
	cmd += '4544'

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

	if 'Windows' in platform.system():
		# work around a hidapi bug in Windows which drops the first byte
		i = int('00'+s, 16)
		dev.write(i.to_bytes(65, byteorder='big'))
	else:
		i = int(s, 16)
		dev.write(i.to_bytes(64, byteorder='big'))


################################################################################
################################################################################


def calc_crc(data):
	# This is the standard CRC algorithm, with the paramaters tweaked to what's
	# used here. This implementation is based off of:
	#   https://gist.github.com/Lauszus/6c787a3bc26fea6e842dfb8296ebd630
	data = bytearray.fromhex(data)
	crc = 0
	for bit in data:
		crc ^= bit
		for _ in range(8):
			crc <<= 1
			if crc & 0x100:
				crc ^= 0x101
	# trim off the '0x' that hex() adds, and pad with a leading 0 if needed
	crc = hex(crc)[2:]
	if len(crc) == 1:
		return '0' + crc
	return crc


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
