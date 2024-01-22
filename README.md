> For a 64-bit (code only) alternative one could look at https://github.com/solo-fsw/vuams-markers

# vu_ams
vu-ams plug-in for the [smathot/OpenSesame](https://github.com/smathot/OpenSesame) project

# Install

Copy the folder "vu_ams" to the OpenSesame plugins folder (for Windows 10 x64 normally "C:\Program Files (x86)\OpenSesame\share\opensesame_plugins\" ). Restart OpenSesame if it was already running.
Please see http://osdoc.cogsci.nl/manual/environment for more information on OpenSesame and plug-ins.

# About

The vu_ams plug-in sends event markers from OpenSesame to the VU-AMS device (www.vu-ams.nl) to mark events in the VU-AMS data. These events can be used for analyzing the VU-AMS data. For example by automatically creating labels based on the event markers send by OpenSesame.

# Dependencies

The vu_ams plug-in uses the 32 bit AmsSerial.dll to communicate with the VU-AMS device. Therefore it will only work on Windows with a 32 bit version of OpenSesame. The last 32 bit version of OpenSesame can be found [here](https://github.com/smathot/OpenSesame/releases/tag/release%2F3.2.8). Download a **win32** version at the bottom of the page. 
The AmsSerial.dll should be installed with the latest version of [VU-DAMS](http://www.vu-ams.nl/support/downloads/software) that you will need to install to configure the VU-AMS device anyway. You can also find a dedicated AmsSerial.dll installer at www.vu-ams.nl/support/downloads/extras

# More

Please see [vu_ams.md](vu_ams/vu_ams.md) for more information


