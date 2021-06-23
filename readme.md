This program lets you control the bias lighting LEDs on the LG 27gn950 monitor under Linux and Windows (and maybe also Mac? - should work, but untested).

It requires Python 3 and the pyusb library as dependencies: `pip3 install pyusb`, or use the `python-pyusb` package on Arch Linux

On Windows, you will also need to install the libusb backend for the PyUSB library. Full setup instructions here: https://github.com/subraizada3/27gn950controller/issues/2#issuecomment-866204669


Usage on Linux, and probably also Mac:
- To get a command line interface, do: `$ sudo ./control.py`
  - Enter 'h' for help / command reference
- To get a GUI, do: `$ sudo ./gui.py` or `$ sudo ./control.py gui`
  - If you download a zip from GitHub instead of doing a git clone, the gui.py file/shortcut will not work. You can either:
    - run the gui as `sudo ./control.py gui`, or
    - fix the shortcut by deleting gui.py and then making a copy of the control.py file named gui.py (the script will detect the filename and launch the gui instead of the cli)


Usage on Windows:
- To get a command line interface, you can either:
  - open a command prompt, navigate to this folder, and run: `python control.py`
  - or double click the control.py file from File Explorer
  - Enter 'h' for help / command reference
- To get the gui, you can either:
  - open a command prompt, navigate to this folder, and run: `python control.py gui`
  - or double click the gui.bat file from File Explorer


To control the main monitor brightness (of the screen), see:
  https://www.subraizada.com/blog/ddc/


Running noninteractively:
- Any CLI command can be added as a command line argument. For example, to turn on your monitor's lighting you would normally run the CLI and enter 'turnOn'. Instead, you can run:
  - `sudo ./control.py turnOn` (Linux)
  - `python control.py turnOn` (Windows)

Multimonitor support:
- By default, all monitors will be controlled. You can manually specify a monitor number in the GUI by entering a number in the text box. Note that numbering starts at 0; if you have three monitors they are numbered (0, 1, 2).
- In the CLI, prefix your command with the monitor number and a comma. Otherwise all monitors will be controlled. For example, instead of using `turnOn`, use `2,turnOn` to turn on the 3rd monitor. This format also works when running noninteractively.
