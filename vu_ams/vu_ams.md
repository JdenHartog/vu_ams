# vu_ams items

`vu_ams` items allow you to send event markers to a VU-AMS device (<http://www.vu-ams.nl>).

## Options

You can specify a number of options:

- *Device name* "COM3" for example ("autodetect" by default). Note the Device name from the first vu_ams item is used and the Device name fields of the following vu_ams items are ignored.
- *Send marker* The marker number to send. Value between 0 and 65535. Also a variable like "[AMSmarker]" can be used.
- *Use number from title* The marker number to send will be extracted from the item title.
- *Use without VU-AMS device* This will allow you to try the experiment without a VU-AMS device while developing. Use by ticking the checkbox in the first vu_ams item in your experiment. Caution: No markers will be sent to the VU-AMS device; use for debugging only! 

## Note

It is advisable to insert a logger item after the vu_ams item(s), typically at the end of your trial sequence. This will allow you to log the marker_sent_time(s) that you may need in case the connection to the VU-AMS device is lost during the experiment.
