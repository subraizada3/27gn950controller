#!/usr/bin/env python3

# Copyright © 2021 Subramaniyam Raizada
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# TODO: allow sending a single command (not interactive) with `./control.py 57`
# TODO: organize separation between command line control and API


import sys

import tkinter as tk

import usb.core
import usb.util


dev = usb.core.find(idVendor=0x043e, idProduct = 0x9a8a)
if dev is None:
	print('Device not found')
	sys.exit(0)

for cfg in dev:
	for intf in cfg:
		if dev.is_kernel_driver_active(intf.bInterfaceNumber):
			try:
				dev.detach_kernel_driver(intf.bInterfaceNumber)
			except usb.core.USBError as e:
				sys.exit('Cound not detach kernel driver from interface ({0}): {1}'.format(intf.bInterfaceNumber, str(e)))

dev.set_configuration()
cfg = dev.get_active_configuration()

# send commands to device
def sendStr(data):
	sendInt(int(data, 16))

def sendInt(data):
	dev.write(2, data.to_bytes(64, byteorder='big'))



controlCodes = {
	'turnOn':       ('e01020000.d', 'f02020100.e'),
	'turnOff':      ('e01020000.d', 'f02020200.d'),
	'set1':         ('702020001.6', 'a02020301.8'),
	'set2':         ('702020002.5', 'a02020302.b'),
	'set3':         ('702020003.4', 'a02020303.a'),
	'set4':         ('702020004.3', 'a02020304.d'),
	'setPeaceful':  ('702020005.2', 'a02020305.c'),
	'setDynamic':   ('702020006.1', 'a02020306.f'),
	'setVideoSync': ('702020008.f', 'a02020308.1'),
	'macroY':       ('801020000.b', 'e01020000.d'), # unused
	'macroX':       ('b01020000.8', 'c01020000.f'), # unused
}

def sendControlCode(code):
	part1 = '5343c'
	part3 = '4544000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
	part2_1 = controlCodes[code][0].replace('.', 'd')
	part2_2 = controlCodes[code][1].replace('.', 'd')
	sendStr(part1 + part2_1 + part3)
	sendStr(part1 + part2_2 + part3)

def sendBrightnessCode(brt):
	if brt < 1 or brt > 12:
		return
	part1 = '5343c'
	part2_1 = 'f0202010'
	brts = {
		1: '1.f',
		2: '2.c',
		3: '3.d',
		4: '4.a',
		5: '5.b',
		6: '6.8',
		7: '7.9',
		8: '8.6',
		9: '9.7',
		10: 'a.4',
		11: 'b.5',
		12: 'c.2',
	}
	part2_2 = brts[brt].replace('.', 'd')
	part3 = '4544000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
	sendStr(part1 + part2_1 + part2_2 + part3)

def sendRawStr(code):
	sendStr(code)

def launchCli():
	helpstring = '''Command reference:
Exit: q / exit / EOF / ctrl-c
Help: h / help / ?
Commands:
  1-12                   - set brightness
  turnOn turnOff         - turn LEDs on or off
  set1 set2 set3 set4    - activate a preset slot
  setPeaceful setDynamic - builtin RGB cycle modes
  setVideoSync           - swap to video sync mode; sync itself is not implemented yet
Not yet implemented:
  Changing RGB colors saved into the 1/2/3/4 slots
  Syncing video after entering video sync mode\
'''

	while True:
		try:
			code = input().strip()
		except KeyboardInterrupt as e:
			print()
			sys.exit(0)
		except EOFError as e:
			sys.exit(0)
		if code == '' or code == 'q' or code == 'exit':
			sys.exit(0)
		elif code == 'h' or code == 'help' or code == '?':
			print(helpstring)
		elif len(code) <= 2:
			sendBrightnessCode(int(code))
		elif len(code) == 128:
			sendRawStr(code)
		elif code in controlCodes.keys():
			sendControlCode(code)
		else:
			print('invalid')

class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.master = master
		self.pack()
		self.create_widgets()

	def create_widgets(self):
		controlBtnsContainer = tk.Frame(self)
		controlCodeButtons = [
			# x, y, text, command
			(0, 0, 'On', 'turnOn'),
			(0, 1, 'Off', 'turnOff'),
			(1, 0, 'Color 1', 'set1'),
			(1, 1, 'Color 2', 'set2'),
			(1, 2, 'Color 3', 'set3'),
			(1, 3, 'Color 4', 'set4'),
			(2, 0, 'Peaceful', 'setPeaceful'),
			(2, 1, 'Dynamic', 'setDynamic'),
			(2, 2, 'Video Sync', 'setVideoSync'),
		]
		for btnDef in controlCodeButtons:
			btn = tk.Button(controlBtnsContainer)
			btn['text'] = btnDef[2]
			# closure hack because python sucks
			btn['command'] = lambda btnDef=btnDef: sendControlCode(btnDef[3])
			btn.grid(row=btnDef[0], column=btnDef[1])
		controlBtnsContainer.pack(side='top')

		spacer = tk.Label(self)
		spacer.pack(side='top')

		# brightness buttons
		brightnessBtnsContainer = tk.Frame(self)
		for i in range(1, 13):
			btn = tk.Button(brightnessBtnsContainer)
			btn['text'] = str(i)
			btn['command'] = lambda i=i: sendBrightnessCode(i)
			btn.grid(row=3, column=i)
		brightnessBtnsContainer.pack(side='top')

def launchGui():
	root = tk.Tk()
	app = Application(master=root)
	app.mainloop()

if ('gui' in sys.argv[0].lower()) or (len(sys.argv) > 1 and 'gui' in sys.argv[1].lower()):
	launchGui()
else:
	launchCli()
