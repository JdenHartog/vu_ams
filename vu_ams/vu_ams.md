# vu_ams items

`vu_ams` items allow you to send event markers to a VU-AMS device (<http://www.vu-ams.nl>).

## Options

You can specify a number of options:

- *Device name* "COM3" for example ("autodetect" by default).
- *Send marker* The marker number to send. Value between 0 and 65535. Also a variable like "[AMSmarker]" can be used.

## Note

It is advisable to insert a logger item after the vu_ams item(s), typically at the end of your trial sequence. This will allow you to log the marker_sent_time(s) that you may need in case the connection to the VU-AMS device is lost during the experiment.
