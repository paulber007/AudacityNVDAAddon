#appModules/audacity.py

import appModuleHandler
import winUser
import controlTypes
import os
import gui
import wx
import ui
import api
from NVDAObjects.window import Window
from NVDAObjects.IAccessible import IAccessible
import time
import addonHandler
from audacity_docHandler import openDocPath
from  objects import isPressed, inTracksPanelView
import timerControl
import ou_time

addonHandler.initTranslation()


# timer to monitor audio and selection changes
GB_monitorTimer = None
# audio position  monitor

GB_audioPosition = None
# selection monitor
GB_selection = None
# record button state monitor
GB_recordButtonPressed = None



_addonDir = os.path.join(os.path.dirname(__file__), "..").decode("mbcs") # The root of an addon folder
_curAddon = addonHandler.Addon(_addonDir) # Addon instance
_addonSummary = _curAddon.manifest['summary']
_addonVersion = _curAddon.manifest['version']
_addonName = _curAddon.manifest['name']
_scriptCategory = unicode(_addonSummary)


MONITOR_TIMER_DELAY = 500



def monitorAudioAndSelectionChanges():
	global GB_monitorTimer, GB_audioPosition, GB_selection, GB_recordButtonPressed
	
	obj = api.getFocusObject()
	if not inTracksPanelView(obj):
		GB_monitorTimer = wx.CallLater(MONITOR_TIMER_DELAY, monitorAudioAndSelectionChanges)
		return
			
	
	recordButtonPressed = isPressed("record")
	if not recordButtonPressed and GB_recordButtonPressed:
		ui.message(_("Record stopped"))
		time.sleep(0.5)
	elif recordButtonPressed and not GB_recordButtonPressed:
		ui.message(_("Record"))
		time.sleep(0.5)

		
	GB_recordButtonPressed = recordButtonPressed

	if  (recordButtonPressed
		or (isPressed("play") and not isPressed("pause"))
		):
		GB_monitorTimer = wx.CallLater(MONITOR_TIMER_DELAY, monitorAudioAndSelectionChanges)
		return
	
	
	# audio
	audioTimer = timerControl.AudioTimerControl()
	newAudioPosition = audioTimer.getAudioPosition()
	if newAudioPosition != GB_audioPosition :
		audioTimer.sayAudioPosition()

	GB_audioPosition = newAudioPosition
	# selection
	selectionTimer = timerControl.SelectionTimers()
	newSelection = selectionTimer.getSelection()
	if GB_selection == None:
		GB_selection = newSelection
		
	((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), durationChoice) = newSelection
	((selectionStartLabel, oldSelectionStartTime), (selectionEndLabel, oldSelectionEndTime), durationChoice) = GB_selection
	# change to no selection ?
	if ((selectionStartTime != oldSelectionStartTime 
		or selectionEndTime != oldSelectionEndTime)
		and selectionTimer.sayIfNoSelection(selectionStartTime, selectionEndTime)):
		pass
		
	else:
		# no
		if selectionStartTime != oldSelectionStartTime and not audioTimer.sayIfAudioAtStartOfSelection (GB_audioPosition, newSelection):
			selectionTimer.saySelectionStart(newSelection)
		if selectionEndTime != oldSelectionEndTime:
			selectionTimer.saySelectionEnd(newSelection)

			
	GB_selection = newSelection
	# timer restart 	
	GB_monitorTimer = wx.CallLater(MONITOR_TIMER_DELAY, monitorAudioAndSelectionChanges)
	
	

class TimerControlEdit(IAccessible):
	def event_gainFocus(self):
		timer = timerControl.TimerControl(self)
		(sLabel, sTime) = timer.getLabelAndTime()
		ui.message(sLabel)
		ou_time.sayTime(sTime)


	def check(cls, obj= None):
		#print ("timerControlEdit check", obj.role, obj.childCount)
		if obj == None:
			obj = api.getFocusObject()
		

		if (obj.role != controlTypes.ROLE_STATICTEXT or obj.childCount <6):
			return False
			
		timer = timerControl.TimerControl(obj)
		return timer.check()

		
	check = classmethod(check)
	
class TimerControlDigit(IAccessible):
	_digitTypes = (
		_("hour"),_("hour"), 
		_("minute"), _("minute"),
		_("second"),_("second"),
		None, None, None,
		)
		
	_digitNames = (
		_("hour ten"),
		_("hours unit"),
		_("minutes ten"),
		_("minutes unit"),
		_("seconds ten"),
		_("seconds unit"),
		_("seconds tenth"),
		_("seconds hundredth"),
		_("seconds thousandth")
		)

	def _get_name(self):
		name = super(TimerControlDigit, self)._get_name()
		name = name.replace(" ", "")
		return name.split(",")[-1]

		
	def event_nameChange(self):
		pass


	def event_gainFocus(self):
		#print "TimerControlDigit gainFocus"
		name = self._get_name()
		digitID = self.getId() -1
		if len(name) > 1:
			# only with up and down arrow
			type = self._digitTypes[digitID]
			if type == None:
				type = (_("tenth"), _("hundredth"), _("thousandth"))[len(name)-1]
			if name[0] =="0":
				name = name[1:] 
			
			ui.message(u"{0} {1}" .format(name, type))


			return
		
		digitName = self._digitNames[digitID]
		text = name.replace("h", "|")
		text = text.replace("m","|")
		text = text.replace("s", "|")
		
		ui.message(u"{0} {1}" .format(digitName, text.split("|")[-1]))

	
	def getId(self):
		try:
			return self.IAccessibleChildID
		except:
			pass
		
		return None




	def check(cls, obj = None):
		if obj == None:
			obj = api.getFocusObject()	
			
		if obj.role == controlTypes.ROLE_STATICTEXT:
			oParent = obj.parent
			if oParent:
				return TimerControlEdit.check(oParent)
		
		return False
	check = classmethod(check)

class Button(IAccessible):
	def initOverlayClass(self):
		self.bindGesture("kb:space", "spaceKey")
		
	def script_spaceKey(self, gesture):
		import eventHandler
		obj = api.getFocusObject()
		try:
			obj.doAction()
		except:
			pass

		eventHandler.queueEvent("gainFocus",obj)





class AppModule(appModuleHandler.AppModule):
	
	def __init__(self, *args, **kwargs):

		super(AppModule, self).__init__(*args, **kwargs)

		
		# set help menu
		self.help = gui.mainFrame.sysTrayIcon.helpMenu
		self.helpItem = self.help.Append(wx.ID_ANY, u"{summary} {version}".format(summary=_addonSummary, version=_addonVersion), _addonName)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onHelp, self.helpItem)
		
	def onHelp(self, evt):
		openDocPath()		
		
	def terminate(self):
		try:
			self.help.RemoveItem(self.helpItem)
		except wx.PyDeadObjectError:
			pass
			
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.role == controlTypes.ROLE_BUTTON:
			clsList.insert(0, Button)

		elif TimerControlEdit.check(obj):
			clsList.insert(0, TimerControlEdit)
		
		elif TimerControlDigit.check(obj):
			clsList.insert(0, TimerControlDigit)
	

	def event_appModule_gainFocus(self):
		global GB_monitorTimer, GB_audioPosition, GB_selection, GB_recordButtonPressed, GB_recordMonitorTimer
		GB_audioPosition = None
		GB_selection = None
		GB_recordButtonPressed = None
		# start monitor timer
		GB_monitorTimer = wx.CallLater(MONITOR_TIMER_DELAY, monitorAudioAndSelectionChanges)


	def event_appModule_loseFocus(self):
		global GB_monitorTimer, GB_recordMonitorTimer
		if GB_monitorTimer != None:
			GB_monitorTimer.Stop()
		GB_monitorTimer = None

			

	

	def event_NVDAObject_init(self,obj):
		if obj.windowClassName=="Button" and not obj.role in [controlTypes.ROLE_MENUBAR, controlTypes.ROLE_MENUITEM, controlTypes.ROLE_POPUPMENU]:
			obj.name=winUser.getWindowText(obj.windowHandle).replace('&','')
			
			
	def script_testAudacity(self, gesture):
		print "test audacity"
		ui.message("test audacity")

	





		









	def script_reportAudioPosition (self, gesture):
		timer = timerControl.AudioTimerControl()
		timer.sayAudioPosition()

	script_reportAudioPosition.__doc__ = _("report audio position")
	script_reportAudioPosition.category = _scriptCategory

	def script_reportSelection (self, gesture):		
		timer = timerControl.SelectionTimers()
		timer.saySelection()
	script_reportSelection.__doc__ = _("report start and end of selection")
	script_reportSelection.category = _scriptCategory

	def script_reportTransportButtonsState(self, gesture):
		if isPressed("record"):
			ui.message(_("record button pressed"))
			return
			
	
	
		if isPressed("play"):
			ui.message(_("play button pressed"))
			if isPressed("pause"):
				ui.message(_("Pause button pressed"))
				
		else:
			ui.message(_("Play button released"))
			
	


	script_reportTransportButtonsState.__doc__ = _("report the state of Pause and Play buttons")
	script_reportTransportButtonsState.category = _scriptCategory
	

		
	__gestures ={
		#"kb:control+alt+f10":"testAudacity",
		"kb:control+shift+s": "reportSelection",
		"kb:control+shift+t": "reportAudioPosition",
		"kb:alt+control+f5": "reportTransportButtonsState"
		}