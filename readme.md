This program lets you control the bias lighting LEDs on the LG 27GN950 monitor under Linux and Windows, and probably also macOS (untested). It supports multiple monitors and implements full functionality aside from editing the preset colors and running video sync (for now).


### Setup

This requires Python 3 and the PyUSB library as dependencies.

For Windows, full setup instructions are available [here](https://github.com/subraizada3/27gn950controller/blob/master/docs/windows-setup.md).

Linux setup: Install the PyUSB library for Python: `sudo pip3 install pyusb`. You'll also need the `libusb` library on your system. There's a very high chance you already have libusb installed, but if not, you should be able to install through your package manager (apt/dnf/etc.). On Arch Linux you can simply install the `python-pyusb` and `libusb` packages with Pacman; no other setup is required.

MacOS: Setup should be very similar to Linux, but the exact commands you have to run may vary. I believe the libusb library is available through the brew package manager.

### Usage

On Linux, and probably also Mac:
- You will need to run every command with `sudo` unless you [add a udev rule](https://github.com/subraizada3/27gn950controller/blob/master/docs/udev-setup.md).
- To get a command line interface, do: `./control.py`
  - Enter 'h' for help / command reference
- To get a GUI, do: `./gui.py` or `./control.py gui`
  - If you download a zip from GitHub instead of doing a git clone, the gui.py file/shortcut will not work properly. You can either:
    - Run the gui as `./control.py gui`, or
    - Fix the shortcut: delete gui.py; then make a copy of the control.py file named gui.py. Now you can run gui.py to get the gui.

On Windows:
- To get a command line interface, you can either:
  - open a command prompt, navigate to this folder, and run: `python control.py`
  - or double click the control.py file from File Explorer
  - Enter 'h' for help / command reference
- To get the gui, you can either:
  - open a command prompt, navigate to this folder, and run: `python control.py gui`
  - or double click the gui.bat file from File Explorer

To control the main monitor brightness (of the screen), see:
  https://www.subraizada.com/blog/ddc/

### Multimonitor

Multimonitor support:
- By default, all monitors will be controlled. You can manually specify a monitor number in the GUI by entering a number in the text box. Note that numbering starts at 0; if you have three monitors they are numbered (0, 1, 2).
- In the CLI, prefix your command with the monitor number and a comma. Otherwise all monitors will be controlled. For example, instead of using `turnOn`, use `2,turnOn` to turn on the 3rd monitor. This format also works when running noninteractively.

### Noninteractive mode / automation

Running noninteractively:
- Any CLI command can be added as a command line argument. For example, to turn on your monitor's lighting you would normally run the CLI and enter 'turnOn'. Instead, you can run:
  - `sudo ./control.py turnOn` (Linux)
  - `python control.py turnOn` (Windows)
