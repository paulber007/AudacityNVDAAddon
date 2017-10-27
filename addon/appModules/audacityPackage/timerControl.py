import addonHandler
addonHandler.initTranslation()
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
import queueHandler







	
	


def sayMessage(msg):
	api.processPendingEvents()
	ui.message(msg)
	
	
class TimerControl(object):
	def __init__(self, obj, ):
		self.obj = obj
		self.name = obj.name


	
	def getLabelAndTime(self):
		timerControlName = self.name
		if len(timerControlName) < 18:
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
		obj = objects.objectAudioPosition()
		if not obj:
			# error
			print "error, not audioPositionObject"
			return
			
		super(AudioTimerControl, self).__init__(obj)



	def getAudioPosition(self):
		return self.getLabelAndTime()
	

	
	def sayAudioPosition(self):
		sAudioPosition = self.getLabelAndTime()
		if   sAudioPosition == None :
			#error
			return
	
			
		(sAudioPositionLabel,sAudioPositionTime) = sAudioPosition
		selection = SelectionTimers().getSelection()
		if selection == None:
			return

		((sSelectionStartLabel, sSelectionStartTime),(sSelectionEndLabel, sSelectionEndTime), idurationChoice) = selection
		if not isNullDuration(sSelectionStartTime)and self.sayIfAudioAtStartOfSelection(sAudioPosition, selection):
			pass
	
		else:
			# not selection  or selection at start of track
			if isNullDuration(sAudioPositionTime):
				# audio at track start
				sayMessage( _("Audio position at start of track"))
			else:
				sayMessage(sAudioPositionLabel)
				sayTime(sAudioPositionTime)
	
	
	
	
	
	

	def sayIfAudioAtStartOfSelection(self, sAudioPosition, selection):
		(sAudioPositionLabel, sAudioPositionTime) = sAudioPosition
		((sSelectionStartLabel, sSelectionStartTime),(sSelectionEndLabel, sSelectionEndTime), idurationChoice) = selection
		if not isNullDuration(sSelectionStartTime):
			# there is a selection and  selection start is not start of track
			if (sAudioPositionTime == sSelectionStartTime
				or isNullDuration(sAudioPositionTime)):
				# start of audio position  at start of selection
				api.processPendingEvents()
				sayMessage(_("Audio position at selection's start"))
				sayTime(sSelectionStartTime)
				return True
		return False

class SelectionStartTimerControl(TimerControl):
	def __init__(self):
		obj = objects.objectSelectionStart()
		super(SelectionStartTimerControl, self).__init__(obj)

	def getSelection(self):
		return  self.getLabelAndTime()

		
class SelectionEndTimerControl(TimerControl):
	def __init__(self):
		obj = objects.objectSelectionEnd()
		super(SelectionEndTimerControl, self).__init__(obj)
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

	def saySelection(self, selection = None):
		if selection == None:
			selection = self.getSelection()


			
		if selection == None:
			return 
		# say start and end of selection
		((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), durationChoice) = selection
		if self.sayIfNoSelection(selectionStartTime, selectionEndTime):
			return
			
		sayMessage(selectionStartLabel)
		sayTime(selectionStartTime)
		sayMessage(selectionEndLabel)
		sayTime(selectionEndTime)
			
	def sayIfNoSelection(self, selectionStartTime, selectionEndTime):
		if (selectionStartTime == selectionEndTime) and isNullDuration(selectionStartTime):
			sayMessage(_("no selection"))
			return True
		return False
				
	
	def saySelectionStart(self, selection = None):
		if selection == None:
			selection= self.getSelection()

				
		if selection == None:
			return
			
		((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), durationChoice) = selection
		sayMessage (selectionStartLabel)
		sayTime(selectionStartTime)
		
	
	
	
	def saySelectionEnd(self, selection = None):
		if selection == None:
			selection = getSelection()
		if selection == None:
			return
		
		((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), durationChoice) = selection
		
		sayMessage(selectionEndLabel)
		sayTime(selectionEndTime)
	
