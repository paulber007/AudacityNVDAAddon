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
from  objects import isPressed







	
	


def sayMessage(msg):
	api.processPendingEvents()
	ui.message(msg)
	
	
class TimerControl(object):
	def __init__(self, obj = None):
		if obj is not None:
			self.obj = obj
		self.name = self.obj.name
	
	def getLabelAndTime(self):
		if self.obj is None:
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


	def check(self):
		if self.obj is None:
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
		self.obj = objects.audioPositionObject()
		if self.obj is None:
			# error
			log.warning("error, not audioPositionObject")
		super(AudioTimerControl, self).__init__()

	def getAudioPosition(self):
		return self.getLabelAndTime()
	
	def getAudioPositionMessage(self):
		if self.obj is None:
			return None
		sAudioPosition = self.getLabelAndTime()
		if   sAudioPosition == None :
			#error
			return None
		(sAudioPositionLabel,sAudioPositionTime) = sAudioPosition
		selection = SelectionTimers().getSelection()
		if selection == None:
			return None
		
		((sSelectionStartLabel, sSelectionStartTime),(sSelectionEndLabel, sSelectionEndTime), idurationChoice) = selection
		msg = self.getIfAudioAtStartOfSelectionMessage(sAudioPosition, selection)
		if not isNullDuration(sSelectionStartTime)and msg is not None:
			pass
		else:
			# not selection  or selection at start of track
			if isNullDuration(sAudioPositionTime):
				# audio at track start
				msg =_("Audio position at start of track")
			else:
				msg = sAudioPositionLabel
				msg = "%s %s"%(msg, getTimeMessage(sAudioPositionTime))
		return msg
		return None
	
	def getIfAudioAtStartOfSelectionMessage(self, sAudioPosition, selection):
		msg = None
		(sAudioPositionLabel, sAudioPositionTime) = sAudioPosition
		((sSelectionStartLabel, sSelectionStartTime),(sSelectionEndLabel, sSelectionEndTime), idurationChoice) = selection
		if not isNullDuration(sSelectionStartTime):
			# there is a selection and  selection start is not start of track
			if (sAudioPositionTime == sSelectionStartTime
				or isNullDuration(sAudioPositionTime)):
				# start of audio position  at start of selection
				msg="%s %s" %(_("Audio position at selection's start"), getTimeMessage(sSelectionStartTime))
		return msg

class SelectionStartTimerControl(TimerControl):
	def __init__(self):
		self.obj = objects.selectionStartObject()
		if self.obj is None:
			log.error ("no selectionStart object")
			return
		super(SelectionStartTimerControl, self).__init__()

	def getSelection(self):
		return  self.getLabelAndTime()

		
class SelectionEndTimerControl(TimerControl):
	def __init__(self):
		self.obj = objects.selectionEndObject()
		if self.obj is None:
			log.error("no selectionEnd object")
			return
		super(SelectionEndTimerControl, self).__init__()
	
	def getSelection(self):
		return  self.getLabelAndTime()

class SelectionTimers(object):
	def __init__(self):
		self.selectionStart = SelectionStartTimerControl()
		self.selectionEnd = SelectionEndTimerControl()
		self.iDurationChoice = objects.isChecked("durationChoice")



	
	def getSelection(self):
		selectionStart = self.selectionStart.getLabelAndTime()
		selectionEnd = self.selectionEnd.getLabelAndTime()
		return (selectionStart, selectionEnd, self.iDurationChoice)
	
	def getSelectionMessage(self, selection = None):
		if selection == None:
			selection = self.getSelection()
		
		if selection == None:
			return  None
		# say start and end of selection
		((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), durationChoice) = selection
		if self.sayIfNoSelection(selectionStartTime, selectionEndTime):
			return None
		textList = []
		textList.append(selectionStartLabel)
		textList.append(getTimeMessage(selectionStartTime))
		textList.append(selectionEndLabel)
		textList.append(getTimeMessage(selectionEndTime))
		return " ".join(textList)

			
	def sayIfNoSelection(self, selectionStartTime, selectionEndTime):
		if (selectionStartTime == selectionEndTime) and isNullDuration(selectionStartTime):
			sayMessage(_("no selection"))
			return True
		return False
				
			
	def getIfNoSelectionMessage(self, selectionStartTime, selectionEndTime):
		if (selectionStartTime == selectionEndTime) and isNullDuration(selectionStartTime):
			return _("no selection")
		return None
	
	def getSelectionStartMessage(self, selection = None):
		if selection == None:
			selection= self.getSelection()
		
		if selection == None:
			return None
		
		((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), durationChoice) = selection
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
		
		((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), durationChoice) = selection
		return "%s %s" %(selectionEndLabel, getTimeMessage(selectionEndTime))
