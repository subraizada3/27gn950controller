This program lets you control the bias lighting LEDs on the LG 27GN950 monitor, without needing to use the official LG software. This program has no affiliation with LG.

This program supports all functionality of the official LG software, except for video sync mode, which is currently under development.

This program can also control multiple 27GN950 monitors connected to your system.

This project also provides a library that other applications can use to control 27GN950 monitors. See the `lib27gn950.py` file for details and documentation.

### Current status

This project previously provided a graphical application that could be used to control the monitor. After the recent v2 rewrite (which added support for video sync mode to the backend library, and added macOS support) the GUI needs to be re-made for the new codebase.

| OS | Normal controls | Multi-monitor | GUI | Video sync |
|----|-----------------|---------------|-----|------------|
| Linux | Functional | Untested, but should work | In development | In development |
| Windows | Functional | Untested, but should work | In development | In development |
| macOS | Untested, but should work | Untested, but should work | In development | In development |

### Setup

This requires Python 3, the Python HID package, and the HIDAPI library as dependencies.

##### Linux
On Arch Linux: `sudo pacman -S hidapi python-hid`

On other Linuxes:
- Install the Python HID package, for your user and root:
  - `pip3 install --user hid`
  - `sudo pip3 install --user hid`
- Install the HIDAPI library. See https://pypi.org/project/hid/ for commands for various distributions.

##### Windows
- The HIDAPI dll is included in this repository, so you don't have to install it separately.
- Install Python from [python.org/downloads](https://www.python.org/downloads/). When installing, make sure to check the checkbox for the 'Add Python to PATH' option on the bottom of the initial screen, and then click the 'Disable path length limit' button at the end of the installation.
- Install the Python HID library by opening Windows PowerShell and running:
  - `py -m pip install hid`
- Download this repository, extract the zip file, open the folder and double click on `console.py`
  - Make sure the LG software isn't running at the same time
  - Type 'help' for a list of commands

##### MacOS (untested, I don't have an Apple computer):
- Install the HIDAPI library
  - `brew install hidapi`
- Install the Python HID package
  - `pip3 install --user hid`
  - `sudo pip3 install --user hid`

### Usage

- To get a command line interface, do: `sudo ./console.py`
  - Enter `help` for help / command reference
- The GUI needs to be recreated for the new codebase (TODO)

To control the monitor brightness (of the screen, not the bias lighting), see:
  https://www.subraizada.com/blog/ddc/

### Multimonitor

Multimonitor support:
- By default, all monitors will be controlled. You can manually specify which monitors you want to control using the `info` and `select` commands in the command line interface.

### Noninteractive mode / automation

Any CLI command can be provided as a command line argument. For example, to turn on your monitor's lighting you would normally run the CLI and enter 'turn_on'. Instead, you can run:

`sudo ./console.py turn_on`

By default, that command will apply to all monitors. You can select specific monitors to apply the command to by prepending them to the command, comma-separated. For example:

- To turn off monitor 2: `sudo ./console.py 2,turn_off`
- To set the color of static color slot 2 to green, only on monitors 1 and 3: `sudo ./console.py 1,3,set 2 00ff00`
