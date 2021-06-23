These steps were sufficient to get the program to work in a fresh Windows installation:

- Install Python from [https://www.python.org/](https://www.python.org/) => there's a download button in the popup when you hover over the Downloads button in the navigation bar
  - When you run the installer, make sure to check the box to add Python to the PATH. Also click the button to increase the maximum path length before exiting the installer.
- Open a command prompt and run `py -m pip install pyusb` to install the PyUSB library

Now the libusb backend needs to be installed - this allows PyUSB to talk to Windows's USB subsystem.

- Download the latest release from [https://github.com/libusb/libusb/releases](https://github.com/libusb/libusb/releases). The first asset, `libusb-1.0.24.7z` contains the correct files.
- For some reason libusb distributes their Windows version as a 7zip file instead of a normal zip file, so if you don't already have 7zip you'll need to install it from [https://www.7-zip.org/download.html](https://www.7-zip.org/download.html). The second download link, for the 64-bit x64 exe should work.
- Then, open your downloads folder in the file explorer, right click the libusb 7z file you downloaded, and extract it.
- From the extracted files, go into the `VS2019` folder and then into the `MS64` folder and then into the `dll` folder. In here is a file called `libusb-1.0.dll`. Copy that dll into `C:\Windows\System32`.
- Run the control.py file as described in the readme, and it should work.

---

There's a chance that it will not work, especially if you have multiple monitors. In that case, you will have to manually change the driver association of the USB device from LG's Ultragear Control Center over to libusb.

- First, completely exit out of LG Ultragear Control Center (from the taskbar, if it's running).
- Download Zadig, a USB driver installer/configurator, from [https://zadig.akeo.ie/](https://zadig.akeo.ie/).
- Open Zadig, in the Options menu at the top click 'List All Devices'
- Select the LG monitor from the list. It'll show a 'HidUsb' driver on the left; go ahead and replace it with WinUSB.

![image](https://user-images.githubusercontent.com/3249268/123026557-622dc580-d3aa-11eb-8e67-502c93bad552.png)

- Do that for every 27GN950 on your system, if you have multiple. They should now show up in device manager (right click the start menu icon => 5th option). In my case, it's at the very bottom. Maybe also re-plug their USB just to be on the safe side.

![image](https://user-images.githubusercontent.com/3249268/123026626-8093c100-d3aa-11eb-9d8c-345717654ef6.png)

Then you can run control.py again and it should work properly. If not, you can double click the device in Device Manager, go to the Driver tab and Roll Back the drivers, which will undo the modifications from Zadig and allow the LG control center to work again. Using the libusb-win32 drivers, as described at [https://github.com/subraizada3/27gn950controller/issues/2#issuecomment-866480021](https://github.com/subraizada3/27gn950controller/issues/2#issuecomment-866480021), might resolve the issue.
