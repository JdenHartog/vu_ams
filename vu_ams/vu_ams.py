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

from libopensesame.py3compat import *

from libopensesame import debug
from libopensesame.exceptions import osexception
from libopensesame.item import item

from libqtopensesame.items.qtautoplugin import qtautoplugin

from openexp.canvas import canvas
from openexp.keyboard import keyboard

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
		self.var._device_name = u'autodetect'
		self.var._send_marker = 1
		self.var._use_title_checkbox = u'no' # yes = checked, no = unchecked
		self.var._use_without_vu_ams = u'no' # yes = checked, no = unchecked
		
		self.var._vuams = 'None'

	def prepare(self):

		"""The preparation phase of the plug-in goes here."""
		
		# Check if vuamsconnected is 'debug' so all vu_ams actions and warnings are skipped. This will work for all 
		# vu_ams items that follow the vu_ams item where "Use without VU-AMS device" is checked
		# NOTE: the behaviour might be a bit strange when vu_ams is used in a loop item: http://osdoc.cogsci.nl/usage/prepare-run/
		try: 
			if(self.experiment.get(u'vuamsconnected') == u'debug'):
				return
			# Check if "Use without VU-AMS device" is checked. Then set vuamsconnected to 'debug' so all vu_ams actions and warnings are skipped
			elif(self.var._use_without_vu_ams ==  u'yes'):
				self.experiment.set(u'vuamsconnected',u'debug')
				self.warn()
				print u'Item "%s": Debug mode: "Use without VU-AMS device" checked!' % self.name
				return
		except:
			# Check if "Use without VU-AMS device" is checked. Then set vuamsconnected to 'debug' so all vu_ams actions and warnings are skipped
			if(self.var._use_without_vu_ams ==  u'yes'):
				self.experiment.set(u'vuamsconnected',u'debug')
				self.warn()
				print u'Item "%s": Debug mode: "Use without VU-AMS device" checked!' % self.name
				return

		
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
			self.var.AMS = windll.amsserial # requires AmsSerial.dll !!!
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
			if self.var._device_name not in (None, '', u'autodetect'):
				self.var._vuams = self.var._device_name
				try:
					self.var.AMS.Connect(self.var._vuams.encode('utf-8'), 'AMS5fs') #NOTE: port AND device type can't be u'unicode'
					debug.msg(u'Trying to connect to VU-AMS device')
				except Exception as e:
					raise osexception( u'Failed to open device port "%s" : "%s"' % (self.var._vuams, e))

				# Try to get VU-AMS Serial to check is a VU-AMS device is connected
				if(self.var.AMS.GetSerial()<=0):
					raise osexception( u'Failed to connect to device on port "%s"' % (self.var._vuams))

			else:
				# Else determine the common name of the serial devices on the
				# platform and find the first accessible device. On Windows,
				# devices are labeled COM[X], on Linux there are labeled /dev/tty[X]
				debug.msg(u'Trying to connect to VU-AMS device using autodetect')
				if os.name == u'nt':
					for i in range(255):
						try:
							dev = 'COM%d' % (i+1) #as COM ports start from 1 on Windows
							self.var.AMS.Connect(dev, 'AMS5fs') #NOTE: device type AND [dev] can't be u'unicode'
							# Try to get VU-AMS Serial to check is a VU-AMS device is connected
							if(self.var.AMS.GetSerial()>0):
								self.var._vuams = dev
								break
							self.var.AMS.Disconnect()
						except Exception as e:
							self.var._vuams = 'None'

				elif os.name == u'posix':
					raise osexception( \
						u'Sorry: the vu-ams plug-in is Windows only.')
				else:
					raise osexception( \
						u'vu-ams plug-in does not know how to auto-detect the VU-AMS on your platform. Please specify a device.')

			if self.var._vuams == 'None':
				raise osexception( \
					u'vu-ams plug-in failed to auto-detect a VU-AMS. Please specify a device.')
			else:
				self.experiment.set(u'vuamsconnected',u'yes')
				self.experiment.set(u'AMS', self.var.AMS)
				print u'Connected to VU-AMS'
		

			# Check if VU-AMS device is recording
			if(self.var.AMS.IsRecording()!=1):
				raise osexception(u'VU-AMS is not recording!')
			
			# Appending Close to cleanup_functions
			self.experiment.cleanup_functions.append(self.close)

			#######################
			# END: Only ones	###
			#######################


		# If "Use number from title" is enabled get number from item title
		if(self.var._use_title_checkbox ==  u'yes'):
			number = ''.join(x for x in self.name if x.isdigit())
			try:
				int(number)
			except Exception as e:
				raise osexception(u'Item "%s": No number in vu_ams item title "%s" to send as marker' % (self.name, self.name))
			self.set((u'_send_marker'), number)
		
		# Check that title doesn't start with number.
		# Technically this should be a problem but it's not advisable and might be evoked by "Use number from title" functionality.
		if(self.name[0].isdigit()):
			print u'It is not advisable to start an item title with a number. (Good: "vu_ams33", "vu2_ams" and "R2-D2" Bad: "33vu_ams")'
	
		# Check if marker is numerical
		try:
			int(self.get(u'_send_marker'))
		except Exception as e:
			raise osexception(u'Item "%s": Markers must be a number' % self.name)
		# Check if marker is bigger then 65535
		if(self.get(u'_send_marker')>65535):
			raise osexception(u'Item "%s": Markers can not be bigger then 65535' % self.name)
	
		
	def run(self):

		"""The run phase of the plug-in goes here."""

		if(self.experiment.get(u'vuamsconnected') == u'debug'):
			return
		
		self.set_item_onset(self.time())
		
		# takes about 18 milliseconds for AMSi RS232 and 32ms for AMSi USB version
		try:
			print u'Item "%s": Sending marker %s to VU-AMS' % (self.name, self.get(u'_send_marker'))
			self.var.AMS.SendCodedMarker(self.get(u'_send_marker'))
		except:
			print u'Item "%s": Failed to send codedmarker!' % self.name
			
		# set [self.name]_marker_sent_time so it can be stored using the logger item
		try:
			self.experiment.set(u'marker_sent_time_%s' % self.name, str(self.time()))
		except:
			print u'Item "%s": Error set [self.name]_marker_sent_time!' % self.name

			
	def close(self):

		"""Neatly close the connection to the VU-AMS"""
		
		if self.var._vuams == 'None':
				print u'no active vuams'
				return
		try:
			self.var.AMS.Disconnect()
			print u'Closed connection to VU-AMS'
		except:
			print u'failed to close vuams'

			
	def warn(self):

		"""Show screen to warn user that no markers will be send to the VU-AMS device"""
		
		my_canvas = canvas(self.experiment)
		my_canvas.set_font(size=32)
		my_canvas.set_bgcolor(u'yellow')
		my_canvas.clear()
		my_canvas.set_fgcolor(u'red')
		my_canvas.text(u'Warning: <b>no markers</b> will be sent to the VU-AMS! \n\n <i>Hit "c" to Continue or "Esc" to quit</i>')
		my_canvas.show()
		my_keyboard = keyboard(self.experiment)
		my_keyboard.get_key(keylist=[u'c', u'C'])
		my_canvas.set_font(size=21)
		my_canvas.set_bgcolor(u'black')
		my_canvas.clear()
		my_canvas.set_fgcolor(u'purple')
		my_canvas.text(u'Preparing experiment...')
		my_canvas.show()
	
	

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
		# QLineEdit.
		
		# Connect "Send marker" line_edit to "Use number from title" checkbox:
		self.checkbox_widget.stateChanged.connect( \
			self.line_edit_widget2.setDisabled)
		
		# Connect all widgets to "Use without VU-AMS device" checkbox:
		self.checkbox_widget2.stateChanged.connect( \
			self.line_edit_widget.setDisabled)
		self.checkbox_widget2.stateChanged.connect( \
			self.line_edit_widget2.setDisabled)
		self.checkbox_widget2.stateChanged.connect( \
			self.checkbox_widget.setDisabled)