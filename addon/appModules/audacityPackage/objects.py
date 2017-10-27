#audacity/package/objects.py
#Copyright (C) 2015-2017 Paulber19
#This file is covered by the GNU General Public License.
import addonHandler
addonHandler.initTranslation()
from logHandler import log
import api
from oleacc import *
from controlTypes import *

#object hierarchy
HIE_VueDePiste= 1
HIE_LockingTool1 = 2
HIE_LockingTool2 = 3
HIE_TransportToolBar = 4
HIE_PauseButton = 5
HIE_PlayButton = 6
HIE_StopButton = 7
HIE_RecordButton = 8
HIE_SelectionToolBar = 9
HIE_DurationChoice = 10
HIE_SelectionStart = 11
HIE_SelectionEnd = 12
HIE_AudioPosition = 13


# for audacity 2.1.3.0 
hie_2130 = {
	HIE_VueDePiste: "1|1", # from mainFrameObject
	HIE_LockingTool1 : "2|0", # from mainFrameObject
	HIE_LockingTool2 : "3", # from mainFrameObject
	HIE_TransportToolBar : "0", # from HIE_LockingTool1  object
	HIE_PauseButton : "1", # from HIE_TransportToolBar  object
	HIE_PlayButton : "2", # from HIE_TransportToolBar 
	HIE_StopButton : "3", # from HIE_TransportToolBar 
	HIE_RecordButton : "6", # from HIE_TransportToolBar 
	HIE_SelectionToolBar : "0", # from HIE_LockingTool2  object
	HIE_DurationChoice : "5", # from  HIE_SelectionToolBar 
	HIE_SelectionStart : "11", # from  HIE_SelectionToolBar object
	HIE_SelectionEnd : "12", # from HIE_SelectionToolBar object
	HIE_AudioPosition : "14" # from HIE_SelectionToolBar object
	}

hie_2060 = {
	HIE_VueDePiste: "1|1", # from  mainFrameObject
	HIE_LockingTool1 : "2", # from  mainFrameObject
	HIE_LockingTool2 : "3", # from  mainFrameObject
	HIE_TransportToolBar : "0", # from HIE_LockingTool1  object
	HIE_PauseButton : "1", # from HIE_TransportToolBar  object
	HIE_PlayButton : "2", # from HIE_TransportToolBar 
	HIE_StopButton : "3", # from HIE_TransportToolBar 
	HIE_RecordButton : "6", # from HIE_TransportToolBar 
	HIE_SelectionToolBar : "0", # from  HIE_LockingTool2  object
	HIE_DurationChoice : "5", # from HIE_SelectionToolBar 
	HIE_SelectionStart : "11", # from  HIE_SelectionToolBar object
	HIE_SelectionEnd : "12", # from  HIE_SelectionToolBar object
	HIE_AudioPosition : "14" # from HIE_SelectionToolBar object
	}
#for audacity 2.0.3.0

hie_2030 = {
	HIE_VueDePiste: "1|1", # from objectFramePrincipal
	HIE_LockingTool1 : "2", # from ObjectFramePrincipal
	HIE_LockingTool2 : "3", # from  ObjectFramePrincipal
	HIE_TransportToolBar : "0", # from  HIE_VerrouillageDOutils1
	HIE_PauseButton : "1", # from HIE_BarreDOutilsTransport
	HIE_PlayButton : "2", # from HIE_BarreDOutilsTransport
	HIE_StopButton : "3", # from HIE_BarreDOutilsTransport
	HIE_RecordButton : "6", # from HIE_BarreDOutilsTransport
	HIE_SelectionToolBar : "0", # from LockingTool2 Object
	HIE_DurationChoice : "4", # from HIE_BarreDOutilsSelection
	HIE_SelectionStart : "10", # from HIE_BarreDOutilsSelection
	HIE_SelectionEnd : "11", # from HIE_BarreDOutilsSelection
	HIE_AudioPosition : "13" # from HIE_BarreDOutilsSelection
	}
_audacityHierarchyID = None
	
def initialize(appModule):
	global _audacityHierarchyID
	audacityID  = int("".join(appModule._get_productVersion().split(",")))
	if audacityID >= 2130:
		id = hie_2130
	elif audacityID >= 2060:
		id = hie_2060
	else:
		id = hie_2030
	_audacityHierarchyID = id


def getObjectByHierarchy ( oParent, iHierarchy):
	sHierarchy = _audacityHierarchyID[iHierarchy]
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
		if oGParent and oGParent.name.lower() == desktopName:
			return o
		
		o = o.parent
	log.error("error no mainFrameObject")
	return None
	
def lockingTool1Object ():
	o = mainFrameObject()
	if o :
		return getObjectByHierarchy(o, HIE_LockingTool1)
	return None

def  lockingTool2Object():
	o = mainFrameObject()
	if o:
		return  getObjectByHierarchy(o, HIE_LockingTool2)

	return None

def selectionToolBarObject():
	o = lockingTool2Object()
	if o :
		o = getObjectByHierarchy(o, HIE_SelectionToolBar)
		return o
		#return getObjectByHierarchy(o, HIE_SelectionToolBar)
	
	o = mainFrameObject()
	if o:
		o= o.getChild(1)
		count = o.childCount
		while count:
			count = count-1
			if (o.name =="frame"
				and o.getChild(1).name == _("Selection tool bar")):
								return o.getChild(1)

			o = o.next

	return None

def  audioPositionObject():
	o = selectionToolBarObject()
	if o :
		return getObjectByHierarchy(o, HIE_AudioPosition)
		
	return None
def durationChoiceObject ():
	o = selectionToolBarObject()
	if o :
		return getObjectByHierarchy(o, HIE_DurationChoice)

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
def transportToolBarObject ():
	o = lockingTool1Object()
	if o :
		return getObjectByHierarchy(o, HIE_TransportToolBar)

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

def isChecked(check):
	if check == "durationChoice":
		o = durationChoiceObject()
	else:
		# error
		return None
	return STATE_CHECKED in o.states
		
def inTracksPanelView(obj = None):
	if obj == None:
		obj = api.getFocusObject().IAccessibleObject

	if ((obj.role == ROLE_PANE and obj.name == "panel") 
		or (obj.role == ROLE_TABLE and obj.parent.name == "panel")
		or (obj.role == ROLE_TABLEROW and obj.parent.parent.name == "panel")):
		return True
	return False