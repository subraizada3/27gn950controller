Control the bias lighting LEDs on the LG 27gn950 monitor under Linux and Windows (and maybe also Mac?).

Requires Python 3 and pyusb library:
  `pip3 install pyusb`, or use the python-pyusb package on Arch Linux

On Windows, you will also need to install the libusb backend for the PyUSB library:
  https://github.com/subraizada3/27gn950controller/issues/2#issuecomment-866204669


Usage on Linux, and probably also Mac:
  To get a command line interface, do:
  $ sudo ./control.py
  Enter 'h' for help / command reference

  To get a GUI, do:
  $ sudo ./gui.py
  or
  $ sudo ./control.py gui

  If you download a zip from GitHub instead of doing a git clone, the gui.py
    file/shortcut will not work. You can either:
  - run the gui as `sudo ./control.py gui`, or
  - fix the shortcut by deleting gui.py and then making a copy
    of the control.py file named gui.py.


Usage on Windows:
  To get a command line interface, you can either:
  - open a command prompt, navigate to this folder, and run: python control.py
  - or double click the control.py file from File Explorer
  To get the gui, you can either:
  - open a command prompt, navigate to this folder, and run: python control.py gui
  - or double click the gui.bat file from File Explorer


To control the main monitor brightness (of the screen), see:
  https://www.subraizada.com/blog/ddc/
