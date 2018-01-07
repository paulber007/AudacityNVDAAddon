#audacity/audacityPackage/timerControl.py
#Copyright (C) 2015-2017 Paulber19
#This file is covered by the GNU General Public License.
import addonHandler
addonHandler.initTranslation()
from logHandler import log
import controlTypes
import gui
import wx
import ui
import api
from NVDAObjects.window import Window
from NVDAObjects.IAccessible import IAccessible
import time
from ou_time import *
import objects
from  objects import isPressed, selectionChoiceObject

def sayMessage(msg):
	api.processPendingEvents()
	ui.message(msg)

class TimerControl(object):
	def __init__(self, obj = None):
		self.obj = obj
		if obj is None:
			# error
			log.warning("error, not timerControl object %s" %self.__class__)
			
		self.name = self.obj.name  if self.obj is not None else None
	
	def getLabelAndTime(self):
		if not self.isAvailable():
			return("", None)
		timerControlName = self.name
		if not timerControlName or len(timerControlName) < 18:
			return  (timerControlName, None)


		if "+" in timerControlName:
			# +samples
			timerControlName= timerControlName.split("+")[0]
			
		sTemp = timerControlName
		sTemp = sTemp.replace(" ", "")
		sTemp = sTemp.split(".")
		if len(sTemp) == 1:
			#xx h xx m xx s
			i= 14
		else:
			# ** h ** m **.*** s or ** h ** m **.** s
			last = sTemp[-1]
			i = 14 + len(last)
			
		sLabel = timerControlName[:-i]
		sTime = timerControlName[-i:]
		sTime = sTime.replace(" ", "")
		sTime = formatTime(sTime)
		return (sLabel, sTime)

	def isAvailable(self):
		if self.obj is None or len(self.obj.states) == 0 or controlTypes.STATE_INVISIBLE in self.obj.states or controlTypes.STATE_UNAVAILABLE in self.obj.states:
			return False
		return True
	
	
	def check(self):
		if not self.isAvailable():
			return False
		(sLabel, sTime) = self.getLabelAndTime()
		if sTime == None:
			return False
			
		sTemp = ""
		for c in sTime:
			if c in [ "0","1","2","3","4","5", "6", "7","8","9"]:
				sTemp = sTemp+ "*"
			else:
				sTemp = sTemp+c
		if sTemp.lower() in ["**:**:**", "**:**:**.**", "**:**:**.***"]:
			return True
			
		return False

class AudioTimerControl(TimerControl):
	def __init__(self):
		obj = objects.audioPositionObject()
		super(AudioTimerControl, self).__init__(obj)

	def getAudioPosition(self):
		return self.getLabelAndTime()
	
	def getAudioPositionMessage(self):
		if not self.isAvailable():
			return None
		sAudioPosition = self.getLabelAndTime()
		if   sAudioPosition == None :
			#error
			return None
		(sAudioPositionLabel,sAudioPositionTime) = sAudioPosition
		selection = SelectionTimers().getSelection()
		if selection == None:
			return None
		
		((sSelectionStartLabel, sSelectionStartTime),(sSelectionEndLabel, sSelectionEndTime), selectionDuration, selectionCenter) = selection
		msg = self.getIfAudioAtStartOfSelectionMessage(sAudioPosition, selection)
		if not isNullDuration(sSelectionStartTime)and msg is not None:
			pass
		else:
			# not selection  or selection at start of track
			if isNullDuration(sAudioPositionTime):
				# audio at track start
				# Translators: message to the user to inform that audio position is at track start
				msg =_("Audio position at start of track")
			else:
				msg = sAudioPositionLabel
				msg = "%s %s"%(msg, getTimeMessage(sAudioPositionTime))
		return msg
		return None
	
	def getIfAudioAtStartOfSelectionMessage(self, sAudioPosition, selection):
		msg = None
		(sAudioPositionLabel, sAudioPositionTime) = sAudioPosition
		((sSelectionStartLabel, sSelectionStartTime),(sSelectionEndLabel, sSelectionEndTime), selectionDuration, selectionCenter) = selection
		if not isNullDuration(sSelectionStartTime):
			# there is a selection and  selection start is not start of track
			if (sAudioPositionTime == sSelectionStartTime
				or isNullDuration(sAudioPositionTime)):
				# start of audio position  at start of selection
				# Translators: message to the user to inform that the  audio position is at selection start
				msg="%s %s" %(_("Audio position at selection's start"), getTimeMessage(sSelectionStartTime))
		return msg

class SelectionStartTimerControl(TimerControl):
	def __init__(self):
		obj = objects.selectionStartObject()
		if obj is None:
			log.warning ("no selectionStart object")
		super(SelectionStartTimerControl, self).__init__(obj)

	def getSelection(self):
		return  self.getLabelAndTime()

class SelectionEndTimerControl(TimerControl):
	def __init__(self):
		obj = objects.selectionEndObject()
		if obj is None:
			log.warning("no selectionEnd object")
		super(SelectionEndTimerControl, self).__init__(obj)
	
	def getSelection(self):
		return  self.getLabelAndTime()


class SelectionDurationTimerControl(TimerControl):
	def __init__(self):
		obj = objects.selectionDurationObject()

		super(SelectionDurationTimerControl, self).__init__(obj)
	
	def getSelection(self):
		return  self.getLabelAndTime()

class SelectionCenterTimerControl(TimerControl):
	def __init__(self):
		obj = objects.selectionCenterObject()
		super(SelectionCenterTimerControl, self).__init__(obj)
	
	def getSelection(self):
		return  self.getLabelAndTime()

class SelectionTimers(object):
	def __init__(self):
		self.selectionStart = SelectionStartTimerControl()
		self.selectionEnd = SelectionEndTimerControl()
		self.selectionDuration = SelectionDurationTimerControl()
		self.selectionCenter = SelectionCenterTimerControl()
		self.selectionChoice = selectionChoiceObject ()
	def isAvailable (self):
		return  (self.selectionStart and self.selectionEnd) is not None
	
	def getSelection(self):
		selectionStart = self.selectionStart.getLabelAndTime()
		selectionEnd = self.selectionEnd.getLabelAndTime()
		selectionDuration = self.selectionDuration.getLabelAndTime()
		selectionCenter = self.selectionCenter.getLabelAndTime()
		return (selectionStart, selectionEnd, selectionDuration, selectionCenter)
	
	def getSelectionMessage(self, selection = None):
		if selection == None:
			selection = self.getSelection()

		((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), selectionDuration, selectionCenter) = selection
		if (selectionStartTime, selectionEndTime) == (None, None):
			return None
		if self.sayIfNoSelection(selectionStartTime, selectionEndTime):
			return None
		# report start and end of selection
		textList = []
		# Translators: message to user to indicate selection informations
		textList.append(_("Selection: "))
		textList.append(selectionStartLabel)
		textList.append(getTimeMessage(selectionStartTime))
		textList.append(selectionEndLabel)
		textList.append(getTimeMessage(selectionEndTime))
		return " ".join(textList)
	
	def getSelectionDurationMessage(self, selection = None):
		if selection == None:
			selection = self.getSelection()
		if selection == None:
			return  None
		((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), selectionDuration, selectionCenter) = selection
		if selectionDuration[1] is None:
			return None
		(selectionDurationLabel,selectionDurationTime) = selectionDuration 
		textList = []
		# Translators: message to user to indicate selection informations
		textList.append(_("Selection: "))
		textList.append(selectionDurationLabel)
		textList.append(getTimeMessage(selectionDurationTime))
		return " ".join(textList)		
	
	def getSelectionCenterMessage(self, selection = None):
		if selection == None:
			selection = self.getSelection()
		if selection == None:
			return  None		
		((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), selectionDuration, selectionCenter) = selection
		if selectionCenter[1] is None:
			return None
		(selectionCenterLabel,selectionCenterTime) = selectionCenter
		textList = []
		# Translators: message to user to indicate selection informations
		textList.append(_("Selection: "))
		textList.append(selectionCenterLabel)
		textList.append(getTimeMessage(selectionCenterTime))
		return " ".join(textList)		

	
	def sayIfNoSelection(self, selectionStartTime, selectionEndTime):
		if (selectionStartTime == selectionEndTime) and isNullDuration(selectionStartTime):
			# Translators: message to the user to inform that there is no selection
			sayMessage(_("no selection"))
			return True
		return False
	
	def getIfNoSelectionMessage(self, selectionStartTime, selectionEndTime):
		if selectionStartTime == None or selectionEndTime == None:
			return None
		if (selectionStartTime == selectionEndTime) and isNullDuration(selectionStartTime):
			# Translators: message to the user that there is no selection
			return _("no selection")
		return None
	
	def getSelectionStartMessage(self, selection = None):
		if selection == None:
			selection= self.getSelection()
		if selection == None:
			return None
		((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), selectionDuration, selectionCenter) = selection
		textList = []
		#sayMessage (selectionStartLabel)
		textList.append(selectionStartLabel)
		textList.append(getTimeMessage(selectionStartTime))
		return " ".join(textList)
	
	def getSelectionEndMessage(self, selection = None):
		if selection == None:
			selection = getSelection()
		if selection == None:
			return None
		
		((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), selectionDuration, selectionCenter) = selection
		return "%s %s" %(selectionEndLabel, getTimeMessage(selectionEndTime))
