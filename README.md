# vu_ams
vu-ams plug-in for the [smathot/OpenSesame](https://github.com/smathot/OpenSesame) project

# Install

Copy the folder "vu_ams" to the OpenSesame plugins folder (for Windows 7 x64 normally "C:\Program Files (x86)\OpenSesame\share\opensesame_plugins\" ).
Please see http://osdoc.cogsci.nl/manual/environment for more information on OpenSesame and plug-ins.

# About

The vu_ams plug-in sends event markers from OpenSesame to the VU-AMS device (www.vu-ams.nl) to mark events in the VU-AMS data. These events can be used for analyzing the VU-AMS data. For example by automatically creating labels based on the event markers send by OpenSesame.

# Dependencies

The vu_ams plug-in uses the AmsSerial.dll to communicate to the VU-AMS device. Therefore it will only work on Windows.
The AmsSerial.dll should be installed with the latest version of VU-DAMS (www.vu-ams.nl) that you will need to install to configure the VU-AMS device anyway. You can also find a dedicated AmsSerial.dll installer at www.vu-ams.nl/support/downloads/extras

# More

Please see [vu_ams.md](vu_ams/vu_ams.md) for more information


