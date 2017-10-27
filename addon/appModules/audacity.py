#audacity/__init__.py
#Copyright (C) 2015-2017 Paulber19
#This file is covered by the GNU General Public License.
import addonHandler
addonHandler.initTranslation()
from logHandler import log,_getDefaultLogFilePath
import appModuleHandler
import winUser
import controlTypes
import os
import eventHandler
import queueHandler
import gui
import wx
import ui
import speech
import api
from NVDAObjects.window import Window
from NVDAObjects.IAccessible import IAccessible
import time
from  audacityPackage.objects import isPressed, inTracksPanelView
import audacityPackage.timerControl
import audacityPackage.ou_time
import audacityPackage.objects


# timer to monitor audio and selection changes
GB_monitorTimer = None
# audio position  monitor
GB_audioPosition = None
# selection monitor
GB_selection = None
# record button state monitor
GB_recordButtonIsPressed = False


_addonDir = os.path.join(os.path.dirname(__file__), "..").decode("mbcs") # The root of an addon folder
_curAddon = addonHandler.Addon(_addonDir) # Addon instance
_addonSummary = _curAddon.manifest['summary']
_addonVersion = _curAddon.manifest['version']
_addonName = _curAddon.manifest['name']
_scriptCategory = unicode(_addonSummary)

MONITOR_TIMER_DELAY = 400

def monitorAudioAndSelectionChanges(appModule):
	global GB_monitorTimer, GB_audioPosition, GB_selection, GB_recordButtonIsPressed
	def getRecordChangeMessage():
		global GB_recordButtonIsPressed 
		recordButtonIsPressed = isPressed("record")
		msg = None
		if not recordButtonIsPressed and GB_recordButtonIsPressed:
			msg = _("Record stopped")
		elif recordButtonIsPressed and not GB_recordButtonIsPressed:
			msg = _("Record")
		GB_recordButtonIsPressed = recordButtonIsPressed
		return msg
	
	
	def getSelectionChangeMessage(reportSelectionChange):
		global GB_selection
		selectionTimer = audacityPackage.timerControl.SelectionTimers()
		newSelection = selectionTimer.getSelection()
		msgList = []
		if reportSelectionChange:
			if GB_selection == None:
				GB_selection = newSelection
			((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), durationChoice) = newSelection
			((selectionStartLabel, oldSelectionStartTime), (selectionEndLabel, oldSelectionEndTime), durationChoice) = GB_selection
			# change to no selection ?
			msg = selectionTimer.getIfNoSelectionMessage(selectionStartTime, selectionEndTime)
			if ((selectionStartTime != oldSelectionStartTime 
				or selectionEndTime != oldSelectionEndTime)
				and msg is not None):
				msgList.append (msg)
			else:
				# no
				audioTimer = audacityPackage.timerControl.AudioTimerControl()
				msg = audioTimer.getIfAudioAtStartOfSelectionMessage (GB_audioPosition, newSelection)
				if selectionStartTime != oldSelectionStartTime and msg is None:
					msg = selectionTimer.getSelectionStartMessage(newSelection)
					if msg is not None:
						msgList.append(msg)
				if selectionEndTime != oldSelectionEndTime:
					msg = selectionTimer.getSelectionEndMessage(newSelection)
					if msg is not None:
						msgList.append(msg)
		GB_selection = newSelection
		if len(msgList):
			return " ".join(msgList)
		return None
	
	def  getAudioChangeMessage():
		global GB_audioPosition
		audioTimer = audacityPackage.timerControl.AudioTimerControl()
		newAudioPosition = audioTimer.getAudioPosition()
		msg = None
		if newAudioPosition != GB_audioPosition :
			msg = audioTimer.getAudioPositionMessage()
		GB_audioPosition = newAudioPosition
		return msg
	
	obj = api.getFocusObject()
	if not inTracksPanelView(obj):
		GB_monitorTimer = wx.CallLater(MONITOR_TIMER_DELAY, monitorAudioAndSelectionChanges, appModule)
		return
	# record change
	msg = getRecordChangeMessage()
	if msg is not None:
		#ui.message(msg)
		queueHandler.queueFunction(queueHandler.eventQueue, ui.message, msg)
		GB_monitorTimer = wx.CallLater(MONITOR_TIMER_DELAY, monitorAudioAndSelectionChanges, appModule)
		return
	
	if  (GB_recordButtonIsPressed 
		or (isPressed("play") and not isPressed("pause"))):
		# don't speak selection or audio position 
		GB_monitorTimer = wx.CallLater(MONITOR_TIMER_DELAY, monitorAudioAndSelectionChanges, appModule)
		return
	# audio change
	textList = []
	msg = getAudioChangeMessage()
	if msg:
		textList.append(msg)
	
	# selectionchange
	msg = getSelectionChangeMessage(appModule._reportSelectionChange)
	if msg is not None:
		textList.append(msg)
	if len(textList):
		msg = " ".join(textList)
		queueHandler.queueFunction(queueHandler.eventQueue, ui.message, msg)
	GB_monitorTimer = wx.CallLater(MONITOR_TIMER_DELAY, monitorAudioAndSelectionChanges, appModule)


class TimerControlEdit(IAccessible):
	def event_gainFocus(self):
		timer = audacityPackage.timerControl.TimerControl(self)
		(sLabel, sTime) = timer.getLabelAndTime()
		msg = "%s %s" %(sLabel,audacityPackage.ou_time.getTimeMessage(sTime))
		ui.message(msg)

	@classmethod
	def check(cls, obj= None):
		if obj == None:
			obj = api.getFocusObject()
		
		if (obj.role != controlTypes.ROLE_STATICTEXT or obj.childCount <6):
			return False
			
		timer = audacityPackage.timerControl.TimerControl(obj)
		return timer.check()
	
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
	
	@classmethod
	def check(cls, obj = None):
		if obj == None:
			obj = api.getFocusObject()	
			
		if obj.role == controlTypes.ROLE_STATICTEXT:
			oParent = obj.parent
			if oParent:
				return TimerControlEdit.check(oParent)
		
		return False


class Button(IAccessible):
	def initOverlayClass(self):
		self.bindGesture("kb:space", "spaceKey")
		
	def script_spaceKey(self, gesture):
		obj = api.getFocusObject()
		try:
			obj.doAction()
		except:
			pass

		eventHandler.queueEvent("gainFocus",obj)

class AppModule(appModuleHandler.AppModule):
	
	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		audacityPackage.objects.initialize(self)
		self._reportFocusOnToolbar = False
		self._reportSelectionChange = True
	
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.role == controlTypes.ROLE_BUTTON:
			clsList.insert(0, Button)

		elif TimerControlEdit.check(obj):
			clsList.insert(0, TimerControlEdit)
		
		elif TimerControlDigit.check(obj):
			clsList.insert(0, TimerControlDigit)
	
	def event_appModule_gainFocus(self):
		global GB_monitorTimer, GB_audioPosition, GB_selection, GB_recordButtonIsPressed
		GB_audioPosition = None
		GB_selection = None
		GB_recordButtonIsPressed = None
		# start monitor timer
		GB_monitorTimer = wx.CallLater(MONITOR_TIMER_DELAY, monitorAudioAndSelectionChanges, self)


	def event_appModule_loseFocus(self):
		global GB_monitorTimer
		if GB_monitorTimer != None:
			GB_monitorTimer.Stop()
		GB_monitorTimer = None
	
	def event_NVDAObject_init(self,obj):
		if obj.windowClassName=="Button" and not obj.role in [controlTypes.ROLE_MENUBAR, controlTypes.ROLE_MENUITEM, controlTypes.ROLE_POPUPMENU]:
			obj.name=winUser.getWindowText(obj.windowHandle).replace('&','')
	def event_gainFocus(self, obj, nextHandler):			
		if self._reportFocusOnToolbar:
			self.reportFocusOnToolbar(obj)
			self._reportFocusOnToolbar = False
		nextHandler()
	
	def script_reportAudioPosition (self, gesture):
		timer = audacityPackage.timerControl.AudioTimerControl()
		msg = timer.getAudioPositionMessage()
		if msg is not None:
			ui.message(msg)


	script_reportAudioPosition.__doc__ = _("report audio position")
	script_reportAudioPosition.category = _scriptCategory

	def script_reportSelection (self, gesture):		
		timer = audacityPackage.timerControl.SelectionTimers()
		msg = timer.getSelectionMessage()
		if msg is not None:
			ui.message(msg)
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
	

	def script_toggleSelectionChangeReport(self, gesture):
		self._reportSelectionChange = not self._reportSelectionChange
		if self._reportSelectionChange:
			speech.speakMessage(_("Report selection change"))
		else:
			speech.speakMessage(_("Don't report selection change"))
	script_toggleSelectionChangeReport.__doc__ = _("Toggle selection change report")
	script_toggleSelectionChangeReport.category = _scriptCategory
	def reportFocusOnToolbar(self, focus):
		o = focus.parent
		while o:
			if o.role == 3 and  o.name != "panel":
				ui.message(o.name)
				break
			o = o.parent
		
		

	def script_reportFocusOnToolbar(self, gesture):
		self._reportFocusOnToolbar = True
		gesture.send()


	
	
	__gestures ={
		"kb:control+shift+s": "reportSelection",
		"kb:control+shift+t": "reportAudioPosition",
		"kb:alt+control+f5": "reportTransportButtonsState",
		"kb:alt+control+f4" : "toggleSelectionChangeReport",
		"kb:control+f6": "reportFocusOnToolbar",
		"kb:shift+control+f6": "reportFocusOnToolbar"
		}