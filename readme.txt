Control the bias lighting LEDs on the LG 27gn950 monitor under Linux (and maybe other OSs?).

Requires Python 3 and pyusb library:
  `pip3 install pyusb`, or use the python-pyusb package on Arch Linux

Usage:
  To get a command line interface, do:
  $ sudo ./control.py
  Enter 'h' for help / command reference

  To get a GUI, do:
  $ sudo ./gui.py
  or
  $ sudo ./control.py gui


To control the main monitor brightness (of the screen) you can use the standard
  DDC protocol via the ddcutil progam ('ddcutil' package in Arch).
Example, create file 'brt' with contents:
  #!/bin/sh
  sudo modprobe i2c-dev
  sudo ddcutil setvcp 10 $1 &
Then, run `./brt 57`, etc. - valid values are 0-100.
