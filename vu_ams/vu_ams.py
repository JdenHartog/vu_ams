#-*- coding:utf-8 -*-

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame.item import item
from libqtopensesame.items.qtautoplugin import qtautoplugin

from libopensesame.exceptions import osexception
from libopensesame import debug
import os


class vu_ams(item):

	"""
	This class (the class with the same name as the module) handles the basic
	functionality of the item. It does not deal with GUI stuff.
	"""

	# Provide an informative description for your plug-in.
	description = u'Connect to VU-AMS device and send marker'

	def reset(self):

		"""
		desc:
			Resets plug-in to initial values.
		"""

		# Here we provide default values for the variables that are specified
		# in info.json. If you do not provide default values, the plug-in will
		# work, but the variables will be undefined when they are not explicitly
		# set in the GUI.
		self._device_name = u'autodetect'
		self._send_marker = 1
		
		self._vuams = None

	def prepare(self):

		"""The preparation phase of the plug-in goes here."""

		# Call the parent constructor.
		item.prepare(self)

		# Several parts of the preparations only have to happen ones (i.e. not for every vu_ams item in the exp):
		# 1) Loading the dll 
		# 2) Connecting to the device
		# 3) Checking if device is recording
		# 4) Appending Close to cleanup_functions
		# Because the item.py get and set functions can only handle simple variable types (unicode, float, int);
		# we can not store the <class 'ctypes.WinDLL'> returned by windll.amsserial globally.
		# Therefore we load the dll (1) in every prepare. Luckily it seems to return the same handle every time. 
		# To track if the device is already connected (so 2, 3 and 4 can be skipped) we use the global variable
		# vuamsconnected.

		
		# Load dll to communicate with VU-AMS device
		try:
			from ctypes import windll
			self.AMS = windll.amsserial # requires AmsSerial.dll !!!
			debug.msg(u'Loaded AmsSerial.dll')
		except:
			raise osexception( \
				u'AmsSerial.dll not found. Download (and install) from www.vu-ams.nl >  support  >  downloads  >  extra  >  Download AMS serial DLL setup version 1.3.5 ')
		
		try:
			self.experiment.get(u'vuamsconnected')
		except:
			#######################
			# Only ones:
			#######################
			
			# If a device has been specified, use it
			if self._device_name not in (None, '', u'autodetect'):
				self._vuams = self._device_name
				try:
					self.AMS.Connect(str(self._vuams), 'AMS5fs') #NOTE: device type can't be u'unicode'
					debug.msg(u'Trying to connect to VU-AMS device')
				except Exception as e:
					raise osexception( u'Failed to open device port "%s" : "%s"' % (self._vuams, e))

				# Try to get VU-AMS Serial to check is a VU-AMS device is connected
				if(self.AMS.GetSerial()<=0):
					raise osexception( u'Failed to connect to device on port "%s"' % (self._vuams))

			else:
				# Else determine the common name of the serial devices on the
				# platform and find the first accessible device. On Windows,
				# devices are labeled COM[X], on Linux there are labeled /dev/tty[X]
				debug.msg(u'Trying to connect to VU-AMS device using autodetect')
				if os.name == u'nt':
					for i in range(255):
						try:
							dev = u'COM%d' % (i+1) #as COM ports start from 1 on Windows
							self.AMS.Connect(str(dev), 'AMS5fs') #NOTE: device type can't be u'unicode'
							# Try to get VU-AMS Serial to check is a VU-AMS device is connected
							if(self.AMS.GetSerial()>0):
								self._vuams = dev
								break
							self.AMS.Disconnect()
						except Exception as e:
							self._vuams = None
							pass

				elif os.name == u'posix':
					raise osexception( \
						u'Sorry: the vu-ams plug-in is Windows only.')
				else:
					raise osexception( \
						u'vu-ams plug-in does not know how to auto-detect the VU-AMS on your platform. Please specify a device.')

			if self._vuams == None:
				raise osexception( \
					u'vu-ams plug-in failed to auto-detect a VU-AMS. Please specify a device.')
			else:
				self.experiment.set(u'vuamsconnected',u'yes')
				print u'Connected to VU-AMS'
		

			# Check if VU-AMS device is recording
			if(self.AMS.IsRecording()!=1):
				raise osexception(u'VU-AMS is not recording!')
			
			# Appending Close to cleanup_functions
			self.experiment.cleanup_functions.append(self.close)

			#######################
			# END: Only ones	###
			#######################


		# Check if marker is numerical
		try:
			int(self.get(u'_send_marker'))
		except Exception as e:
			raise osexception(u'Number')
		# Check if marker is bigger then 65535
		if(self.get(u'_send_marker')>65535):
			raise osexception(u'Markers can not be bigger then 65535')
	
		
	def run(self):

		"""The run phase of the plug-in goes here."""
		
		# takes about 18 milliseconds for AMSi RS232 and 32ms for AMSi USB version
		try:
			print u'Sending marker %s to VU-AMS' % (self.get(u'_send_marker'))
			self.AMS.SendCodedMarker(self.get(u'_send_marker'))
			# set [self.name]_marker_sent_time so it can be stored using the logger item
			self.experiment.set(u'%s_marker_sent_time' % self.name, str(self.time()))
		except:
			print u'### Failed to send codedmarker!'
			
	def close(self):

		"""Neatly close the connection to the VU-AMS"""
		
		if self._vuams == None:
				print u'no active vuams'
				return
		try:
			self.AMS.Disconnect()
			print u'Closed connection to VU-AMS'
		except:
			print u'failed to close vuams'



class qtvu_ams(vu_ams, qtautoplugin):
	
	"""
	This class handles the GUI aspect of the plug-in. By using qtautoplugin, we
	usually need to do hardly anything, because the GUI is defined in info.json.
	"""

	def __init__(self, name, experiment, script=None):

		"""
		Constructor.
		
		Arguments:
		name		--	The name of the plug-in.
		experiment	--	The experiment object.
		
		Keyword arguments:
		script		--	A definition script. (default=None)
		"""

		# We don't need to do anything here, except call the parent
		# constructors.
		vu_ams.__init__(self, name, experiment, script)
		qtautoplugin.__init__(self, __file__)

	def init_edit_widget(self):

		"""
		Constructs the GUI controls. Usually, you can omit this function
		altogether, but if you want to implement more advanced functionality,
		such as controls that are grayed out under certain conditions, you need
		to implement this here.
		"""

		# First, call the parent constructor, which constructs the GUI controls
		# based on info.json.
		qtautoplugin.init_edit_widget(self)
		# If you specify a 'name' for a control in info.json, this control will
		# be available self.[name]. The type of the object depends on the
		# control. A checkbox will be a QCheckBox, a line_edit will be a
		# QLineEdit. Here we connect the stateChanged signal of the QCheckBox,
		# to the setEnabled() slot of the QLineEdit. This has the effect of
		# disabling the QLineEdit when the QCheckBox is uncheckhed.
		#self.checkbox_widget.stateChanged.connect( \
		#	self.line_edit_widget.setEnabled)


