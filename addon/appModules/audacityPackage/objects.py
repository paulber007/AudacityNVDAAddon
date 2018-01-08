# -*- coding: UTF-8 -*-
#appModules/audacityPackage/objects.py
# a part of audacity add-on
# Author: paulber19
# Copyright 2016-2017, released under GPL.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()
from logHandler import log
import api
import gui
import wx
from oleacc import *
from controlTypes import *

#object hierarchy
HIE_TrackView= 1
HIE_ToolDock1  = 2
HIE_ToolDock2 = 3
HIE_TransportToolBar = 4
HIE_PauseButton = 5
HIE_PlayButton = 6
HIE_StopButton = 7
HIE_RecordButton = 8
HIE_SelectionToolBar = 9
HIE_AudioPosition = 10
HIE_SelectionChoice = 11
HIE_SelectionStart = 12
HIE_SelectionEnd = 13
HIE_SelectionDuration = 14
HIE_SelectionCenter =  15
HIE_AudacityTranscriptionToolbar = 16
HIE_PlaybackSpeedSlider = 17
HIE_RecordMeterPeak = 18
HIE_PlayMeterPeak = 19
HIE_SliderRecording = 20
HIE_SliderPlayback= 21


# for audacity 2.2.0 
hie_2200 = {
	HIE_TrackView: "1|0", # from mainFrameObject
	HIE_ToolDock1 : "2|0", # from mainFrameObject
	HIE_PauseButton : "1", # from HIE_TransportToolBar  object
	HIE_PlayButton : "2", # from HIE_TransportToolBar 
	HIE_StopButton : "3", # from HIE_TransportToolBar 
	HIE_RecordButton : "6", # from HIE_TransportToolBar 
	HIE_PlaybackSpeedSlider: "3|2", #  from HIE_ToolDock1
	HIE_RecordMeterPeak: "1", # from HIE_RecordingMeterToolbar
	HIE_PlayMeterPeak: "1", # from HIE_PlaybackMeterToolbar
	HIE_SliderRecording : "2",# from HIE_MixerToolbar
	HIE_SliderPlayback  :"4", # from HIE_MixerToolbar
	HIE_ToolDock2 : "3", # from mainFrameObject
	HIE_AudioPosition : "11", # from HIE_SelectionToolBar object
	HIE_SelectionChoice : "13", # from  HIE_SelectionToolBar 
	HIE_SelectionStart : "14", # from  HIE_SelectionToolBar object
	HIE_SelectionDuration : "15", # from HIE_SelectionToolBar object
	HIE_SelectionCenter : "16", # from HIE_SelectionToolBar object
	HIE_SelectionEnd : "17", # from HIE_SelectionToolBar object
	}

def initialize(appModule):
	global _audacityHierarchyID
	version = appModule._get_productVersion()
	audacityID  = int("".join(version.split(",")))
	if audacityID >= 2200:
		id = hie_2200
	else:
		log.warning(_("This version %s of Audacity is not  compatible with the add-on")%version)
		wx.CallLater(1000, gui.messageBox,
			# Translators: the label of a message box dialog.
			_("This version %s of Audacity is not  compatible with the add-on")%version,			# Translators: the title of a message box dialog.
			_("Audacity add-on  warning"),
			wx.OK|wx.ICON_WARNING)
		id = None
	_audacityHierarchyID = id


def getObjectByHierarchy ( oParent, iHierarchy):
	try:
		sHierarchy = _audacityHierarchyID[iHierarchy]
	except:
		return None
	try:
		o = oParent
		if len(sHierarchy):
			Hierarchy = sHierarchy.split("|")
			for i in Hierarchy:
				iChild  = int(i)
				if o and iChild <= o.childCount:
					o = o.getChild(iChild)

				else:
					# error, no child
					return None

			return o
	except:
		log.error("error getObjectByHierarchy: %s, parent: %s" %(sHierarchy, oParent.name))
	return None
	
def mainFrameObject():
	oDesktop = api.getDesktopObject()
	desktopName = oDesktop.name.lower()
	o = api.getFocusObject()
	while o:
		oGParent= o.parent.parent
		if oGParent and oGParent.name and oGParent.name.lower() == desktopName:
			return o
		
		o = o.parent
	log.error("error no mainFrameObject")
	return None
	
def toolDock1Object ():
	o = mainFrameObject()
	if o :
		return getObjectByHierarchy(o, HIE_ToolDock1 )
	return None

def  toolDock2Object():
	o = mainFrameObject()
	if o:
		return  getObjectByHierarchy(o, HIE_ToolDock2)

	return None

def selectionToolBarObject():
	o = toolDock2Object()
	if o :
		#o = getObjectByHierarchy(o, HIE_SelectionToolBar)
		o = o.lastChild
		return o
	return None
def selectionToolBarObject1():
	o = toolDock2Object()
	if o :
		o = getObjectByHierarchy(o, HIE_SelectionToolBar)
		return o
	return None


def  audioPositionObject():
	o = selectionToolBarObject()
	if o  is not None:
		return getObjectByHierarchy(o, HIE_AudioPosition)
		
	return None
def selectionChoiceObject ():
	o = selectionToolBarObject()
	if o :
		return getObjectByHierarchy(o, HIE_SelectionChoice)

	return None

def selectionStartObject ():
	o = selectionToolBarObject()
	if o :
		return  getObjectByHierarchy(o, HIE_SelectionStart)

	return None
	

def selectionEndObject ():
	o = selectionToolBarObject()
	if o :
		return getObjectByHierarchy(o, HIE_SelectionEnd)
	return None
def selectionDurationObject ():
	o = selectionToolBarObject()
	if o :
		return getObjectByHierarchy(o, HIE_SelectionDuration)
	return None
def selectionCenterObject ():
	o = selectionToolBarObject()
	if o :
		return getObjectByHierarchy(o, HIE_SelectionCenter)
	return None

def transportToolBarObject ():
	obj = toolDock1Object ()
	if obj :
		# the only solution to find transport toolbar
		for i in xrange(obj.childCount):
			o = obj.getChild(i)
			if o.childCount == 7:
				return o
		#return getObjectByHierarchy(o, HIE_TransportToolBar)

	return None
def pauseButtonObject ():
	o = transportToolBarObject()
	if o :
		return  getObjectByHierarchy(o, HIE_PauseButton)

	return None
def playButtonObject ():
	o = transportToolBarObject()
	if o :
		return getObjectByHierarchy(o, HIE_PlayButton)

	return None
	
def stopButtonObject():
	o = transportToolBarObject()
	if o :
		return getObjectByHierarchy(o, HIE_StopButton)
	return None
		
def recordButtonObject():
	o = transportToolBarObject()
	if o :
		return getObjectByHierarchy(o, HIE_RecordButton)
	return None

_buttonObjectsDic = {
		"play": playButtonObject,
		"pause" : pauseButtonObject,
		"stop": stopButtonObject,
		"record": recordButtonObject
		}

def isPressed( button):
	try:
		o = _buttonObjectsDic[button]()
	except:
		log.warning("Button %s not found"%button)
		o =None
	
	if o and o.IAccessibleObject.accState(0) & STATE_SYSTEM_PRESSED :
		return True
	return False



def isAvailable( button):
	try:
		o = _buttonObjectsDic[button]()
	except:
		log.warning("Button %s not found"%button)
		o =None
	
	if o and (o.IAccessibleObject.accState(0) & STATE_SYSTEM_UNAVAILABLE  or o.IAccessibleObject.accState(0) & STATE_SYSTEM_INVISIBLE ):
		return False
	return True

def recordingMeterToolbarObject():
	o = transportToolBarObject()
	if o :
		return o.next.next
	return None

def recordMeterPeakObject():
	o = recordingMeterToolbarObject()
	if o :
		return getObjectByHierarchy(o, HIE_RecordMeterPeak)
	return None
def playbackMeterToolbarObject():
	o = recordingMeterToolbarObject()
	if o :
		return o.next
	return None

def playMeterPeakObject():
	o = playbackMeterToolbarObject()
	if o :
		return getObjectByHierarchy(o, HIE_PlayMeterPeak)
	return None
	
def mixerToolbarObject():
	o = playbackMeterToolbarObject()
	if o :
		return o.next
	return None

def sliderRecordingObject():
	o = mixerToolbarObject()
	if o :
		return getObjectByHierarchy(o, HIE_SliderRecording)
	return None
	
def sliderPlaybackObject():
	o = mixerToolbarObject()
	if o :
		return getObjectByHierarchy(o, HIE_SliderPlayback)
	return None


def transcriptionToolbarObject():
	o = mixerToolbarObject()
	if o :
		return o.next.next
	return None
def playbackSpeedSliderObject():
	o = transcriptionToolbarObject()
	print "o: %s"%o.name
	if o :
		return o.getChild(2)
	return None
