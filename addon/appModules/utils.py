import winUser
import controlTypes
import gui
import wx
from objects import *
from ou_time import *
from oleacc import *
import ui
import addonHandler
addonHandler.initTranslation()

def inTracksPanelView(obj = None):
	if obj == None:
		obj = api.getFocusObject().IAccessibleObject

	if ((obj.role == controlTypes.ROLE_PANE and obj.name == "panel") 
		or (obj.role == controlTypes.ROLE_TABLE and obj.parent.name == "panel")
		or (obj.role == controlTypes.ROLE_TABLEROW and obj.parent.parent.name == "panel")):
		return True

	return False


def sayAudioPosition():
	res = getAudioPosition()
	if   res == None :
		#error
		return
		
	(sAudioPositionLabel,sAudioPositionTime) = res
	res = getSelection()
	if res == None:
		return
	((sSelectionStartLabel, sSelectionStartTime),(sSelectionEndLabel, sSelectionEndTime), idurationChoice) = res

	if not isNullDuration(sSelectionStartTime):
		# there is a selection and  selection start is not start of track
		if (sAudioPositionTime == sSelectionStartTime
			or isNullDuration(sAudioPositionTime)):
			# start of audio position  at start of selection
			ui.message(_("Audio position at selection's start"))
			sayTime(sSelectionStartTime)
		else:
			#; audio position not null
			sAudioPositionTime = formatTime(sAudioPositionTime)
			sayTime(sAudioPositionTime)

	else:
		# not selection  or selection at start of track
		if isNullDuration(sAudioPositionTime):
			# audio at track start
			ui.message( _("Audio position at start of track"))
		else:
			ui.message(sAudioPositionLabel)
			sAudioPositionTime = formatTime(sAudioPositionTime)
			sayTime(sAudioPositionTime)









def getAudioPosition():
	o = objectAudioPosition()
	if not o:
		print "no object AudioPosition"
		return None

	sTime= o.accName(0)[-17:]
	sTime = sTime.replace(" ", "")
	sLabel = o.accName(0)[:-18]
	return (sLabel, sTime)

def getSelection():
	o = objectSelectionStart()
	if not o :
		print"Error, no objectSelectionStart"
		return None


	sTime = o.accName(0)[-17:]
	sTime = sTime.replace(" ", "")
	sLabel = o.accName(0)[:-18]
	sSelectionStart = (sLabel, formatTime(sTime))

	o = objectSelectionEnd()
	if not o :
		print"Error, no objectSelectionEnd"
		return None

	sTime = o.accName(0)[-17:]
	sTime = sTime.replace(" ", "")
	sLabel = o.accName(0)[:-18]
	sSelectionEnd = (sLabel,  formatTime(sTime))

	iDurationChoice = objectDurationChoice().accState(0) & STATE_SYSTEM_CHECKED 
	return (sSelectionStart, sSelectionEnd, iDurationChoice)
def isNullDuration(sDuration):

	sTemp = sDuration.replace(" ", "")
	sTemp = sTemp[:-1]
	sTemp = sTemp.replace("h",":")
	sTemp = sTemp.replace("m",":")
	sTemp = sTemp.split(":")
	sTemp1 = sTemp[2].split(".")

	if len(sTemp1)== 2:
		iTemp = int(sTemp1[0]) + int(sTemp1[1])
	else:
		iTemp = int(sTemp1)


	if (int(sTemp[0])
		or int(sTemp[1])
		or iTemp) :
		return False

	return True
def saySelectionStart():
	res = getSelection()
	if res == None:
		return
		
	((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), durationChoice) = res
	ui.message (selectionStartLabel)
	sayTime(selectionStartTime)
	



def saySelectionEnd():
	res = getSelection()
	if res == None:
		return
	
	((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), durationChoice) = res
	
	ui.message(selectionEndLabel)
	sayTime(selectionEndTime)

def saySelection():
	res = getSelection()
	if res == None:
		return 
	# say start and end of selection
	((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), durationChoice) = res
	if (selectionStartTime == selectionEndTime) and isNullDuration(selectionStartTime):
		ui.message(_("no selection"))
		return
		
	ui.message(selectionStartLabel)
	sayTime(selectionStartTime)
	ui.message(selectionEndLabel)
	sayTime(selectionEndTime)
	
def sayPauseState():
	if isPressed("pause"):
		ui.message(_("pause"))
		sayAudioPosition()
def sayTransportButtonsState():
	if isPressed("pause"):
		ui.message(_("Pause button pressed"))
	if isPressed("play"):
		ui.message(_("play button pressed"))
	else:
		ui.message(_("play stopped"))

		