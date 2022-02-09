This program lets you control the bias lighting LEDs on the LG 27GN950, 38GN950, and 38GL950G monitors without needing to use the official LG software. This program has no affiliation with LG.

This program has the following benefits:
- it supports controlling multiple monitors
- it works on Linux and macOS
- it's lightweight, fast, and has a good UI
- it's free software

![GPLv3 logo](gplv3.png)

Video sync is currenty in development. All other functionality is supported.

This project also provides a library that other applications can use to control the supported monitors. See the `lib27gn950.py` file for details and documentation.

### Current status

| OS | Normal controls | Multi-monitor | GUI | Video sync |
|----|-----------------|---------------|-----|------------|
| Linux | Functional | Untested | Functional | In development |
| Windows | Functional | Untested | Functional | In development |
| macOS | Functional | Untested | Untested | In development |

'Untested' means that it should work. But I only have a single 27GN950 and don't have an Apple computer. If you are able to get this program to successfully work under untested situations, please open an issue and report your success so that this document can be updated.

### Setup

This requires Python 3, the Python HID package, and the HIDAPI library as dependencies.

##### Linux and macOS

On Arch Linux:
- `sudo pacman -S hidapi python-hid python-pyqt5`
- Go to the 'Usage' section below

On other Linuxes and macOS:
- On macOS only, install Python 3 from [python.org/downloads](https://www.python.org/downloads/)
- Install the Python HID package, for your user and root:
  - `pip3 install --user hid`
  - `sudo pip3 install --user hid`
- For the GUI, install the Python PyQt5 package:
  - `pip3 install --user pyqt5`
  - `sudo pip3 install --user pyqt5`
- Install the HIDAPI library:
  - Ubuntu: `sudo apt install hidapi`
  - Fedora: `sudo dnf install hidapi`
  - macOS: `brew install hidapi`
- Go to the 'Usage' section below

##### Windows
- The HIDAPI dll is included in this repository, so you don't have to install it separately.
- Install Python from [python.org/downloads](https://www.python.org/downloads/). When installing, make sure to check the checkbox for the 'Add Python to PATH' option on the bottom of the initial screen, and then click the 'Disable path length limit' button at the end of the installation.
- Install the Python HID library by opening Windows PowerShell and running:
  - `py -m pip install hid`
- For the GUI, install the Python PyQt5 package:
  - `py -m pip install pyqt5`
- Note: if you use Command Prompt instead of PowerShell, run `pip install` instead of `py -m pip install`
- Go to the 'Usage' section below

### Usage

- To get a command line interface, do: `sudo ./console.py`
  - Enter `help` for help / command reference
- To get a graphical interface, do: `sudo ./gui.py`
- On Windows, you can just double click on `console.py` or `gui.pyw` (gui.pyw is the same as gui.py, but it won't open a command prompt window on Windows)

To control the monitor brightness (of the screen, not the bias lighting), see:
  https://www.subraizada.com/blog/ddc/

### Multimonitor

Multimonitor support:
- By default, all monitors will be controlled.
- In the console interface, you can manually specify which monitors you want to control using the `info` and `select` commands in the command line interface.
- In the GUI interface, there are checkboxes to select which monitors to control.

### Noninteractive mode / automation

Any CLI command can be provided as a command line argument. For example, to turn on your monitor's lighting you would normally run the CLI and enter 'turn_on'. Instead, you can run:

`sudo ./console.py turn_on`

By default, that command will apply to all monitors. You can select specific monitors to apply the command to by prepending them to the command, comma-separated. For example:

- To turn off monitor 2: `sudo ./console.py 2,turn_off`
- To set the color of static color slot 2 to green, only on monitors 1 and 3: `sudo ./console.py 1,3,set 2 00ff00`
