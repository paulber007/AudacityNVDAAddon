from logging import log
import api
from oleacc import *
import addonHandler
addonHandler.initTranslation()

#object hierarchy


HIE_ApplicationBarreDeMenus= "3" #par rapport au parent de ObjectFramePrincipal
HIE_MenuLecture = "4|1|1" # par rapport  ObjectApplicationBarreDeMenus
HIE_VueDePiste= "2|1" # par rapport  objectFramePrincipal
HIE_LockingTool1 = "3"# par rapport  ObjectFramePrincipal
HIE_LockingTool2 = "4" # par rapport  ObjectFramePrincipal
HIE_TransportToolBar = "1" # par rapport  HIE_VerrouillageDOutils1
HIE_PauseButton = "2" # par rapport  HIE_BarreDOutilsTransport
HIE_PlayButton = "3" # par rapport  HIE_BarreDOutilsTransport
HIE_StopButton = "4" # par rapport  HIE_BarreDOutilsTransport
HIE_Frame = "5" #par rapport  ObjectFramePrincipal
HIE_SelectionToolBar = "1" # par rapport  HIE_Frame
HIE_ChoixFin = "4" # par rapport  HIE_BarreDOutilsSelection
HIE_DurationChoice = "5" # par rapport  HIE_BarreDOutilsSelection
HIE_SelectionStart = "11" # par rapport  HIE_BarreDOutilsSelection
HIE_SelectionEnd = "12" # par rapport  HIE_BarreDOutilsSelection
HIE_AudioPosition = "14" # par rapport  HIE_BarreDOutilsSelection



def getObjectByHierarchy ( oParent, sHierarchy):
	try:
		o = oParent
		if len(sHierarchy):
			Hierarchy = sHierarchy.split("|")
			for i in Hierarchy:
				iChild  = int(i)
				if o and iChild <= o.accChildCount:
					o = o.accChild(iChild)

				else:
					# error, no child
					return None

			return o
	except:
		log.error("error getObjectByHierarchy")
		
	return None
def objectMainFrame():
	o = api.getForegroundObject().IAccessibleObject
	return o

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
		o= o.accChild(1)
		while o:
			if (o.accName(0) =="frame"
				and o.accChild(1).accName(0) == _("Selection tool bar")):
								return o.accChild(1)

			o = o.accNavigate(NAVDIR_NEXT,0)

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
def isPressed( button):
	buttonsDic = {
		"play": objectPlayButton,
		"pause" : objectPauseButton,
		"stop": objectStopButton
		}
	try:
		o = buttonsDic[button]()
	except:
		print "error, no button"
		return None
	if o.accState(0) & STATE_SYSTEM_PRESSED :
		return True
		
	return False
	
		