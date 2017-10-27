from logHandler import log
import api
from oleacc import *
from controlTypes import *

import addonHandler
addonHandler.initTranslation()

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

hie_2060 = {
	HIE_VueDePiste: "1|1", # par rapport  mainFrameObject
	HIE_LockingTool1 : "2", # par rapport  mainFrameObject
	HIE_LockingTool2 : "3", # par rapport  mainFrameObject
	HIE_TransportToolBar : "0", # par rapport  HIE_LockingTool1  object
	HIE_PauseButton : "1", # par rapport  HIE_TransportToolBar  object
	HIE_PlayButton : "2", # par rapport  HIE_TransportToolBar 
	HIE_StopButton : "3", # par rapport  HIE_TransportToolBar 
	HIE_RecordButton : "6", # par rapport  HIE_TransportToolBar 
	HIE_SelectionToolBar : "0", # par rapport  HIE_LockingTool2  object
	HIE_DurationChoice : "5", # par rapport  HIE_SelectionToolBar 
	HIE_SelectionStart : "11", # par rapport  HIE_SelectionToolBar object
	HIE_SelectionEnd : "12", # par rapport  HIE_SelectionToolBar object
	HIE_AudioPosition : "14" # par rapport  HIE_SelectionToolBar object
	}

	
hie_2030 = {
	HIE_VueDePiste: "1|1", # par rapport  objectFramePrincipal
	HIE_LockingTool1 : "2", # par rapport  ObjectFramePrincipal
	HIE_LockingTool2 : "3", # par rapport  ObjectFramePrincipal
	HIE_TransportToolBar : "0", # par rapport  HIE_VerrouillageDOutils1
	HIE_PauseButton : "1", # par rapport  HIE_BarreDOutilsTransport
	HIE_PlayButton : "2", # par rapport  HIE_BarreDOutilsTransport
	HIE_StopButton : "3", # par rapport  HIE_BarreDOutilsTransport
	HIE_RecordButton : "6", # par rapport  HIE_BarreDOutilsTransport
	HIE_SelectionToolBar : "0", # par rapport  LockingTool2 Object
	HIE_DurationChoice : "4", # par rapport  HIE_BarreDOutilsSelection
	HIE_SelectionStart : "10", # par rapport  HIE_BarreDOutilsSelection
	HIE_SelectionEnd : "11", # par rapport  HIE_BarreDOutilsSelection
	HIE_AudioPosition : "13" # par rapport  HIE_BarreDOutilsSelection
	}



def getObjectByHierarchy ( oParent, iHierarchy):
	appModule = oParent.appModule
	audacityID = int("".join(appModule._get_productVersion().split(",")))
	if audacityID >= 2060:
		hie = hie_2060
	else:
		hie = hie_2030
	sHierarchy = hie[iHierarchy]
	
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
		log.info("error getObjectByHierarchy %s" %sHierarchy)
		
	return None
	
def objectMainFrame():
	
	oDesktop = api.getDesktopObject()
	desktopName = oDesktop.name.lower()

	o = api.getFocusObject()
	while o:
		oGParent= o.parent.parent
		if oGParent and oGParent.name.lower() == desktopName:
			return o
		
		o = o.parent
			
	log.error("error no objectMainFrame")
	return None

		

def objectLockingTool1 ():
	o = objectMainFrame()
	if o :
		return getObjectByHierarchy(o, HIE_LockingTool1)

	return None



def  objectLockingTool2():
	o = objectMainFrame()
	if o:
		return  getObjectByHierarchy(o, HIE_LockingTool2)

	return None


def objectSelectionToolBar():
	o = objectLockingTool2()
	if o :
		return getObjectByHierarchy(o, HIE_SelectionToolBar)



	o = objectMainFrame()
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

def  objectAudioPosition():
	o = objectSelectionToolBar()
	if o :
		return getObjectByHierarchy(o, HIE_AudioPosition)
		
	return None
def objectDurationChoice ():
	o = objectSelectionToolBar()
	if o :
		return getObjectByHierarchy(o, HIE_DurationChoice)

	return None

def objectSelectionStart ():
	o = objectSelectionToolBar()
	if o :
		return  getObjectByHierarchy(o, HIE_SelectionStart)

	return None
	

def objectSelectionEnd ():
	o = objectSelectionToolBar()
	if o :
		return getObjectByHierarchy(o, HIE_SelectionEnd)

	return None
def objectTransportToolBar ():

	o = objectLockingTool1()
	if o :
		return getObjectByHierarchy(o, HIE_TransportToolBar)

	return None
def objectPauseButton ():
	o = objectTransportToolBar()
	if o :
		return  getObjectByHierarchy(o, HIE_PauseButton)

	return None
def objectPlayButton ():
	o = objectTransportToolBar()
	if o :
		return getObjectByHierarchy(o, HIE_PlayButton)

	return None
	
	
def objectStopButton():
	o = objectTransportToolBar()
	if o :
		return getObjectByHierarchy(o, HIE_StopButton)

	return None
		
def objectRecordButton():
	o = objectTransportToolBar()
	if o :
		return getObjectByHierarchy(o, HIE_RecordButton)
		
	return None

_buttonObjectsDic = {
		"play": objectPlayButton,
		"pause" : objectPauseButton,
		"stop": objectStopButton,
		"record": objectRecordButton
		}

def isPressed( button):
	try:
		o = _buttonObjectsDic[button]()
	except:
		pass
		return None
		
	if o and o.IAccessibleObject.accState(0) & STATE_SYSTEM_PRESSED :
		return True
		
	return False

def isChecked(check):
	if check == "durationChoice":
		o = objectDurationChoice()
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