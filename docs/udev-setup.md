Normally you need to run this program as root (with sudo) for it to have permission to access the monitor's USB device to configure lighting. You can add a udev rule to allow all users (not just root) to access just this USB device.

In the directory `/etc/udev/rules.d/`, create a new file called `99-27gn950.rules` with the contents:

```
SUBSYSTEM=="usb", ATTRS{idVendor}=="043e", ATTRS{idProduct}=="9a8a", MODE="666"
```

(The monitor's lighting configuration connection has USB product/vendor ID 043e:9a9a, and MODE="666" allows everything to access it without permission. This is separate from any devices you may have plugged into the two USB ports on the monitor; the rule only affects the lighting control USB device.)

To apply the changes without needing to reboot, run these commands as root:

```
udevadm control --reload
udevadm trigger
```
