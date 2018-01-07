# -*- coding: UTF-8 -*-
from __future__ import unicode_literals # To ensure coding compatibility with python 2 and 3.
#audacity/__init__.py
# a part of audacity appModule
#Copyright (C) 2015-2017 Paulber19
#This file is covered by the GNU General Public License.
# Released under GPL 2

import addonHandler
addonHandler.initTranslation()
from logHandler import log,_getDefaultLogFilePath
import appModuleHandler
import winUser
import controlTypes
import os
import eventHandler
import queueHandler
import scriptHandler
import gui
import wx
import ui
import speech
import api
import NVDAObjects
from NVDAObjects.window import Window
from NVDAObjects.IAccessible import IAccessible
import time
from  audacityPackage.objects import isPressed, isAvailable
import audacityPackage.timerControl
import audacityPackage.ou_time
import audacityPackage.objects
from functools import wraps
import  globalPluginHandler
import tones
from audacityPackage.informationsBox import informationsBox
import winInputHook
from keyboardHandler import internal_keyDownEvent
from audacityPackage.configManager import _addonConfigManager 


# to save current winInputHook keyDownCallback function before hook
_winInputHookKeyDownCallback  = None

# role for audacity
ROLE_TRACKVIEW = 300
ROLE_TRACK = 301
# no label for this role
controlTypes.roleLabels[ROLE_TRACKVIEW] = ""
controlTypes.roleLabels[ROLE_TRACK] = ""



# timer for repeatCount management
GB_taskTimer= None
# timer to monitor audio and selection changes
GB_monitorTimer = None
# audio position  monitor
GB_audioPosition = None
# selection monitor
GB_selection = None
# record button state monitor
GB_recordButtonIsPressed = False


_addonDir = os.path.join(os.path.dirname(__file__).decode("mbcs"), "..") # The root of an addon folder
_curAddon = addonHandler.Addon(_addonDir) # Addon instance
_addonSummary = _curAddon.manifest['summary']
_addonVersion = _curAddon.manifest['version']
_addonName = _curAddon.manifest['name']
_scriptCategory = unicode(_addonSummary)


def monitorAudioAndSelectionChanges():
	global GB_monitorTimer, GB_audioPosition, GB_selection, GB_recordButtonIsPressed
	def getRecordChangeMessage():
		global GB_recordButtonIsPressed 
		recordButtonIsPressed = isPressed("record")
		msg = None
		if not recordButtonIsPressed and GB_recordButtonIsPressed:
			# Translators: message to the user to report state of record button
			msg = _("Recording stopped")
		elif recordButtonIsPressed and not GB_recordButtonIsPressed:
			# Translators: message to the user to report state of record button
			msg = _("Recording")
		GB_recordButtonIsPressed = recordButtonIsPressed
		return msg
	
	
	def getSelectionChangeMessage():
		global GB_selection
		from audacityPackage.configManager import _addonConfigManager 
		selectionTimer = audacityPackage.timerControl.SelectionTimers()
		if not selectionTimer.isAvailable:
			return None
		newSelection = selectionTimer.getSelection()
		msgList = []
		if _addonConfigManager .toggleAutomaticSelectionChangeReportOption(False):
			if GB_selection == None:
				GB_selection = newSelection
			((selectionStartLabel, selectionStartTime), (selectionEndLabel, selectionEndTime), selectionDuration, selectionCenter) = newSelection
			((selectionStartLabel, oldSelectionStartTime), (selectionEndLabel, oldSelectionEndTime), selectionDuration, selectionCenter) = GB_selection
			# change to no selection ?
			msg = selectionTimer.getIfNoSelectionMessage(selectionStartTime, selectionEndTime)
			if ((selectionStartTime != oldSelectionStartTime 
				or selectionEndTime != oldSelectionEndTime)
				and msg is not None):
				msgList.append (msg)
			else:
				# no
				audioTimer = audacityPackage.timerControl.AudioTimerControl()
				if not audioTimer.isAvailable():
					return None
				msg = audioTimer.getIfAudioAtStartOfSelectionMessage (GB_audioPosition, newSelection)
				if msg is None and selectionStartTime != oldSelectionStartTime:
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
		if not audioTimer.isAvailable():
			return None
		newAudioPosition = audioTimer.getAudioPosition()
		msg = None
		if newAudioPosition != GB_audioPosition :
			msg = audioTimer.getAudioPositionMessage()
		GB_audioPosition = newAudioPosition
		return msg
	
	obj = api.getFocusObject()
	if obj.appModule.appName != "audacity" or not obj.appModule.inTrackView(obj, False):
		return

	# record change
	msg = getRecordChangeMessage()
	if msg is not None:
		queueHandler.queueFunction(queueHandler.eventQueue, ui.message, msg)
		return
	
	if  (GB_recordButtonIsPressed 
		or (isPressed("play") and not isPressed("pause"))):
		# don't speak selection or audio position 
		return
	if obj.role == ROLE_TRACKVIEW and obj.childCount == 0:
		# no track in track view, so no selection and audio
		return
	
	# audio change
	textList = []
	msg = getAudioChangeMessage()
	if msg is not None:
		textList.append(msg)
	
	# selectionchange
	msg = getSelectionChangeMessage()
	if msg is not None:
		textList.append(msg)
	if len(textList):
		msg = " ".join(textList)
		queueHandler.queueFunction(queueHandler.eventQueue, ui.message, msg)



def finally_(func, final):
	"""Calls final after func, even if it fails."""
	def wrap(f):
		@wraps(f)
		def new(*args, **kwargs):
			try:
				func(*args, **kwargs)
			finally:
				final()
		return new
	return wrap(final)
	
def stopTaskTimer():
	global GB_taskTimer 
	if GB_taskTimer is not None:

		GB_taskTimer .Stop()
		GB_taskTimer  = None



class Slider(object):
	
	def __init__(self):
		self.obj = None
		
	def isAvailable(self):
		if self.obj is None:
			return False
		states = self.obj.states
		if controlTypes.STATE_UNAVAILABLE in states or controlTypes.STATE_INVISIBLE in states or controlTypes.STATE_FOCUSABLE not in states :
			name = self.obj.name if self.obj.name is not None else ""
			# Translators: message to user to inform  that slider is not available
			msg = _("%s not available")%name
			speech.speakMessage(msg)
			return False
		return True
	def reportLevel(self):
		if not self.isAvailable():
			return 
		name = self.obj.name
		value = self.obj.value
		ui.message("%s: %s"%(name, value))			

class SliderPlayback(Slider):
	def __init__(self):
		self.obj = audacityPackage.objects.sliderPlaybackObject()

class SliderRecording(Slider):
	
	def __init__(self):
		self.obj = audacityPackage.objects.sliderRecordingObject()

class MeterPeak (object):
	def __init__(self):
		self.obj = None
	def isAvailable(self):
		if self.obj is None:
			return False
		states = self.obj.states
		if True or controlTypes.STATE_UNAVAILABLE in states or controlTypes.STATE_INVISIBLE in states or controlTypes.STATE_FOCUSABLE not in states:
			name = self.obj.name if self.obj.name is not None else ""
			if len(name):
				name = " ".join(name.split(" ")[:-2])
				# Translators: message to user to inform that meter peak is not available
			msg = _("%s not available")%name
			speech.speakMessage(msg)
			return False
		return True
	def reportLevel(self):
		if self.obj is None or not self.isAvailable():
			return
		peak = self.obj.name.replace(" - ", ": ")
		ui.message(peak)		
	
	def setFocus(self):
		# nothing works !!!
		def callback():
			#api.moveMouseToNVDAObject( self.obj)
			#api.setMouseObject(self.obj)
			#obj=api.getMouseObject()
			#api.setNavigatorObject(obj)
			#obj=api.getNavigatorObject()
			#obj.setFocus()
			#api.setFocusObject(obj)
			self.obj.IAccessibleObject.accSelect(1,0)
			
		if self.isAvailable():
			wx.CallAfter(callback)


class PlayMeterPeak(MeterPeak):
	def __init__(self):
		self.obj = audacityPackage.objects.playMeterPeakObject()
class RecordMeterPeak(MeterPeak):
	def __init__(self):
		self.obj = audacityPackage.objects.recordMeterPeakObject()
			
	
	
class TrackView (NVDAObjects.NVDAObject):
	def _get_role(self):
		return ROLE_TRACKVIEW

	def event_gainFocus(self):
		super(TrackView, self).event_gainFocus()
		if self.childCount == 0:
			# Translators: message to user that there is no track in tracks view
			ui.message(_("No track"))
		else:
			global GB_monitorTimer, GB_audioPosition, GB_selection, GB_recordButtonIsPressed
			GB_audioPosition = None
			GB_selection = None
			GB_recordButtonIsPressed = None
			wx.CallLater(200, monitorAudioAndSelectionChanges)

class Track(NVDAObjects.NVDAObject):
	def initOverlayClass(self):	
		pass
	
	def _get_role(self):
		return ROLE_TRACK
	
	def _get_states(self):
		states = super(Track,self)._get_states()
		if controlTypes.STATE_SELECTED in states:
			# selection state is already set in name bby audacity , so remove this state
			states.remove(controlTypes.STATE_SELECTED)
		return states


	def event_gainFocus(self):
		super(Track, self).event_gainFocus()

	
	@staticmethod
	def check(obj):
		# check if it is a track in tracks panel view
		try:
			if (obj.role == controlTypes.ROLE_TABLEROW 
				and obj.windowControlID == 1003
				and obj.parent.role == ROLE_TRACKVIEW
				and obj.parent.parent.role == controlTypes.ROLE_PANE
				):
				gParent = obj.parent.parent
				if (gParent.previous.role == controlTypes.ROLE_STATUSBAR):
					return True


		except:
			pass
		return False

	
class TimerControlEdit(NVDAObjects.NVDAObject):
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
	
class TimerControlDigit(NVDAObjects.NVDAObject):
	_digitTypes = (
	# Translators: a part of message to the user when moving with up and down arrow in timer controlnames of 
		_("hour"),_("hour"), 
		_("minute"), _("minute"),
		_("second"),_("second"),
		None, None, None,
		)
		
	_digitNames = (
	# Translators: a part of message to the user when moving with left and right arrow in timer control
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
				# Translators: no comment
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


class Button(NVDAObjects.NVDAObject):
	def initOverlayClass(self):
		from audacityPackage.configManager import _addonConfigManager 
		if _addonConfigManager.toggleUseSpaceBarToPressButtonOption(False):
			self.bindGesture("kb:space", "spaceKey")
			self.bindGesture("kb:Enter", "spaceKey")


	def _get_name(self):
		name = super(Button, self)._get_name()
				# for some bad translated button label 
		return name.replace("&","")



	def script_spaceKey(self, gesture):
		obj = api.getFocusObject()
		try:
			obj.doAction()
		except:
			pass

		eventHandler.queueEvent("gainFocus",obj)


def internal_keyDownEventEx(vkCode,scanCode,extended,injected):
	def startMonitoring():
		global GB_monitorTimer
		if GB_monitorTimer is not None:
			GB_monitorTimer.Stop()
			GB_monitorTimer= None
		GB_monitorTimer = wx.CallLater(250, monitorAudioAndSelectionChanges)
	queueHandler.queueFunction(queueHandler.eventQueue, startMonitoring)
	return _winInputHookKeyDownCallback  (vkCode,scanCode,extended,injected)

class AppModule(appModuleHandler.AppModule):
	# a dictionnary to map  main script to gestures and install feature option
	__shellGestures={}
	_mainScriptToGesture = {
		"moduleLayer": ("kb:nvda+space",),
		"test": ("kb:alt+control+f10",),
		}
	
	_shellScriptToGestures ={
		"displayHelp": ("kb:h",),
		"displayAddonUserManual" : ("kb:g",),
		"displayAudacityGuide" : ("kb:control+g",),
		"reportSelectionLimits": ("kb:s",),
		"reportSelectionDuration": ("kb:shift+s",),
		"reportSelectionCenter": ("kb:control+s",),
		"reportAudioPosition": ("kb:a",),
		"toggleSelectionChangeAutomaticReport": ("kb:f4",),
		"reportTransportButtonsState" : ("kb:f5",),
		"reportPlayMeterPeak": ("kb:f7",),
		"reportRecordMeterPeak": ("kb:f8",),
		"reportSliderPlayback": ("kb:f9",),
		"reportSliderRecording": ("kb:f10",),
		"reportPlaybackSpeed": ("kb:f11",) ,
		}
	
	_scriptsToDocsAndCategory = {
		# Translators: Input help mode message for report selection command
		"reportSelection":  (_("report position of start and end of the selection. Twice: report selection's length. Third: report position of selection's center "), None),
		# Translators: Input help mode message for report selection limits command
		"reportSelectionLimits":( _("Report position of start and end of the selection"), None),
		# Translators: Input help mode message for report selection duration command
		"reportSelectionDuration" : (_("Report selection's length"), None),
		# Translators: Input help mode message for report selection center command
		"reportSelectionCenter" : (_("Report position of selection's center"),None),
		# Translators: Input help mode message for report audio position command
		"reportAudioPosition": (_("report audio position"), None),
		# Translators: Input help mode message for toggle selection change automatic report command
		"toggleSelectionChangeAutomaticReport": (_("Enable or disable automatic report of selection's changes"), None),
		# Translators: Input help mode message for toggle report transport button state command
		"reportTransportButtonsState": (_("report the pressed state of Pause , Play and  Record buttons"), None),
		# Translators: Input help mode message for report playback meter peak command
		"reportPlayMeterPeak": (_("Reports the current level of playback meter peak"), None),
		# Translators: Input help mode message for report record meter peak command
		"reportRecordMeterPeak": (_("Reports the current recording meter peak   level"), None),
		# Translators: Input help mode message for report slider playback command
		"reportSliderPlayback": (_("Reports the current level of playback's slider"), None),
		# Translators: Input help mode message for report slider recording command
		"reportSliderRecording" : (_("Reports the current level of recording's slider"), None),
		# Translators: Input help mode message for report playback speed command
		"reportPlaybackSpeed": (_("Reports the current playback speed level"), None),
		# Translators: Input help mode message for display add-on user manual command
		"displayAddonUserManual": (_("Display add-on user manual"), None),
		# Translators: Input help mode message for display audacity guide command
		"displayAudacityGuide": (_("Display audacity guide"), None),
		# Translators: Input help mode message for launch module layer command
		"moduleLayer":  (_("Launch %s addon 's command shell") %_addonSummary , None),
		# Translators: Input help mode message for display shell command help dialog command
		"displayHelp" : (_("Display commands shell's list"), None),
	}
	
	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		audacityPackage.objects.initialize(self)
		self._reportFocusOnToolbar = False
		self._reportSelectionChange = True
		self.toggling = False
		self.installSettingsMenu()
		self._bindGestures()
		self._setShellGestures()
		wx.CallLater(200,self.installShellScriptDocs)		
		
	def installSettingsMenu(self):
		self.prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
		self.audacityMenu = self.prefsMenu.Append(wx.ID_ANY,
			# Translators: name of the option in the menu.
			_("Audacity add-on's settings")+"...",
			"")
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onAudacityMenu, self.audacityMenu)
	
	def terminate (self):
		if hasattr(self, "checkObjectsTimer") and self.checkObjectsTimer is not None:
			self.checkObjectsTimer.Stop()
			self.checkObjectsTimer = None
		for item in [self.audacityMenu, ]:
			try:
				self.prefsMenu.RemoveItem(item)
			except:
				pass
	
	def onAudacityMenu(self, evt):
		from audacityPackage.configGui import AudacitySettingsDialog
		gui.mainFrame._popupSettingsDialog(AudacitySettingsDialog)

	
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):

		obj.isATrack = Track.check(obj)
		if obj.isATrack:
			clsList.insert(0, Track)
		elif obj.role == controlTypes.ROLE_TABLE and obj.windowControlID == 1003:
			clsList.insert(0, TrackView)
		elif obj.role == controlTypes.ROLE_BUTTON:
			clsList.insert(0, Button)

		elif TimerControlEdit.check(obj):
			clsList.insert(0, TimerControlEdit)
		
		elif TimerControlDigit.check(obj):
			clsList.insert(0, TimerControlDigit)
	

		
		
	
	def event_NVDAObject_init(self,obj):
		pass

	def _bindGestures(self):
		for script, gestures  in self._mainScriptToGesture.iteritems():
			if gestures is None:
				continue
			for gest in gestures:
				self.bindGesture(gest, script)
	
	def _setShellGestures(self):
		for script, gestures in self._shellScriptToGestures.iteritems():
			for gest in gestures:
				self.__shellGestures[gest] = script

	
	def installShellScriptDocs(self):
		for script in self._scriptsToDocsAndCategory .keys():
			(doc, category) = self._getScriptDocAndCategory(script)
			commandText = None
			if script in self._shellScriptToGestures.keys():
				gestures =  self._shellScriptToGestures[script]
				key = gestures[0].split(":")[-1]
				# Translators: message for indicate shell command in input help mode
				commandText = _("(command: %s)")%key


			if commandText is not None:
				doc = "%s %s"%(doc, commandText)
			scr = "script_%s"%script
			func = getattr(self, scr)
			func.im_func.__doc__ = doc
			func.im_func.category = category
			# we must remove documentation of replaced nvda global commands scripts
			if  hasattr(func, "removeCommandsScript") and ((featureID is None) or (featureID and not isInstallWithoutGesture(featureID))):
				globalCommandsFunc = getattr(func, "removeCommandsScript")
				globalCommandsFunc.im_func.__doc__  = None
				
	def _getScriptDocAndCategory(self, script):
		(doc, category) = self._scriptsToDocsAndCategory [script]
		if category is None:
			category = _scriptCategory
		return (doc, category)
		
	def event_appModule_gainFocus(self):
		global GB_monitorTimer, GB_audioPosition, GB_selection, GB_recordButtonIsPressed, _winInputHookKeyDownCallback   
		GB_audioPosition = None
		GB_selection = None
		GB_recordButtonIsPressed = None
		if  winInputHook.keyUpCallback   != internal_keyDownEventEx:
			_winInputHookKeyDownCallback   = winInputHook.keyDownCallback
			winInputHook.setCallbacks(keyDown=internal_keyDownEventEx)
		wx.CallLater(100, monitorAudioAndSelectionChanges)
	
	def event_appModule_loseFocus(self):
		winInputHook.setCallbacks(keyDown= _winInputHookKeyDownCallback  )
		global GB_monitorTimer
		if GB_monitorTimer != None:
			GB_monitorTimer.Stop()
			GB_monitorTimer = None
	
	def event_gainFocus(self, obj, nextHandler):
		if self._reportFocusOnToolbar:
			self.reportFocusOnToolbar(obj)
			self._reportFocusOnToolbar = False
		nextHandler()
	def event_focusEntered(self, obj, nextHandler):
		from audacityPackage.configManager import _addonConfigManager 
		if _addonConfigManager.toggleReportToolbarNameOnFocusEnteredOption(False):
			if obj.name is not None and  obj.role == controlTypes.ROLE_PANE and  obj.name != "panel" and  obj.name != "":
				speech.speakMessage(obj.name)
		nextHandler()
	
	def script_moduleLayer(self, gesture):
		stopTaskTimer()
		# A run-time binding will occur from which we can perform various layered script commands
		# First, check if a second press of the script was done.
		if self.toggling:
			self.script_error(gesture)
			return
		self.bindGestures(self.__shellGestures)
		self.toggling = True
		tones.beep(200, 40)

	def getScript(self, gesture):
		if not self.toggling:
			#script = globalPluginHandler.GlobalPlugin.getScript(self, gesture)
			script = appModuleHandler.AppModule.getScript(self, gesture)
			return script
		#script = globalPluginHandler.GlobalPlugin.getScript(self, gesture)
		script = appModuleHandler.AppModule.getScript(self, gesture)
		if not script:
			script = finally_(self.script_error, self.finish)
		return finally_(script, self.finish)

	def finish(self):
		self.toggling = False
		self.clearGestureBindings()
		self._bindGestures()

	
	def script_error(self, gesture):
		tones.beep(420, 40)


	
	def script_toggleSelectionChangeAutomaticReport(self, gesture):
		from audacityPackage.configManager import _addonConfigManager 
		stopTaskTimer()
		_addonConfigManager .toggleAutomaticSelectionChangeReportOption()
		if _addonConfigManager .toggleAutomaticSelectionChangeReportOption(False):
			# Translators: message to the user when the selection changes
			speech.speakMessage(_("Report automaticaly selection's changes"))
		else:
			# Translators: message to the user when selection change cannot be reported
			speech.speakMessage(_("Don't report automaticaly selection change"))

	def inTrackView(self, obj, notify = True):
		if obj.role in [ROLE_TRACK, ROLE_TRACKVIEW]:
			return True
		if notify:
			# Translators: message to the user when object is not in tracks view
			speech.speakMessage(_("Not in tracks view"))
		return False
	def script_reportAudioPosition (self, gesture):
		stopTaskTimer()
		if not self.inTrackView(api.getFocusObject()):
			return
		timerControl = audacityPackage.timerControl.AudioTimerControl()
		msg = timerControl.getAudioPositionMessage()
		if msg is not None:
			ui.message(msg)
	
	def script_reportSelectionCenter(self, gesture):
		stopTaskTimer()
		if not self.inTrackView(api.getFocusObject()):
			return
		timer = audacityPackage.timerControl.SelectionTimers()
		msg = timer.getSelectionCenterMessage()
		if msg is not None:
			ui.message(msg)
	
	def script_reportSelectionDuration(self, gesture):
		stopTaskTimer()
		if not self.inTrackView(api.getFocusObject()):
			return
		timer = audacityPackage.timerControl.SelectionTimers()
		msg = timer.getSelectionDurationMessage()
		if msg is not None:
			ui.message(msg)
	
	def script_reportSelectionLimits(self, gesture):
		stopTaskTimer()
		if not self.inTrackView(api.getFocusObject()):
			return
		timer = audacityPackage.timerControl.SelectionTimers()
		msg = timer.getSelectionMessage()
		if msg is not None:
			ui.message(msg)

	def script_reportSelection (self, gesture):
		global GB_taskTimer 
		stopTaskTimer()		
		if not self.inTrackView(api.getFocusObject()):
			return
		count = scriptHandler.getLastScriptRepeatCount()
		if count == 0:
			GB_taskTimer = wx.CallLater(200, self.script_reportSelectionLimits, gesture)
		elif count == 1:
			GB_taskTimer = wx.CallLater(200, self.script_reportSelectionDuration, gesture)
		else:
			self.script_reportSelectionCenter( gesture)
	
	def script_reportTransportButtonsState(self, gesture):
		stopTaskTimer()
		if not self.inTrackView(api.getFocusObject()):
			return
		pressed = False
		if isAvailable("record") and isPressed("record"):
			# Translators: message to user when button record is pressed
			ui.message(_("record button pressed"))
			pressed = True
		
		if isAvailable("play") and isPressed("play"):
			# Translators: message to the user when play button is pressed
			ui.message(_("play button pressed"))
			pressed = True
		if isPressed("pause"):
			# Translators: message to the user when pause button is pressed
			ui.message(_("Pause button pressed"))
			pressed = True
				
		if not pressed:
			# Translators: message to the user when no button is pressed
			ui.message(_("No button pressed"))
	
	def script_reportPlaybackSpeed (self,gesture):
		stopTaskTimer()
		if not self.inTrackView(api.getFocusObject()):
			return
		speed = audacityPackage.objects.playbackSpeedSliderObject().value
		ui.message("playback speed: %s"%speed)
	
	def script_reportPlayMeterPeak(self,gesture):
		stopTaskTimer()
		if not self.inTrackView(api.getFocusObject()):
			return
		PlayMeterPeak().reportLevel()
	
	def script_reportRecordMeterPeak(self,gesture):
		stopTaskTimer()
		if not self.inTrackView(api.getFocusObject()):
			return
		RecordMeterPeak().reportLevel()
	
	def script_reportSliderRecording(self, gesture):
		stopTaskTimer()
		if not self.inTrackView(api.getFocusObject()):
			return
		SliderRecording().reportLevel()

	
	def script_reportSliderPlayback(self, gesture):
		stopTaskTimer()
		if not self.inTrackView(api.getFocusObject()):
			return
		SliderPlayback().reportLevel()

	
	def script_displayHelp(self, gesture):
		stopTaskTimer()
		textList = []
		# Translators: header  to display commands 's list
		textList = []
		d = {}
		for script in self._scriptsToDocsAndCategory :
			if script not in self._shellScriptToGestures.keys():
				continue
			gest = self._shellScriptToGestures[script][0]
			if gest in self.__shellGestures:
				(doc, category) = self._scriptsToDocsAndCategory [script]
				key = ":".join(gest.split(":")[1:])
				d[key] = doc
		for key, desc in d.iteritems():
			textList.append("%s: %s"%(desc, key))
		l = []
		l.append(_("Description: command"))
		l.extend(sorted(textList))
		l.append("")
		# Translators: this is the title of informationdialog box  to show help informations
		informationsBox(None, _("Shell Commands's  list"), "\r\n".join(l))
	
	def startFile(self, path):
		# Translators: message for user 
		waitMsg = _("Please wait ...")
		speech.speakMessage(waitMsg)
		os.startfile(path)
	
	def script_displayAddonUserManual (self, gesture):
		stopTaskTimer()
		from languageHandler import curLang
		docPath = os.path.join(_addonDir , "doc")
		manual =  _curAddon.manifest["docFileName"]
		defaultPath = os.path.join(docPath, "en", manual)
		localPath = os.path.join(docPath, curLang, manual)
		if os.path.exists(localPath):
			self.startFile(localPath)
		elif os.path.exists(defaultPath):
			self.startFile(defaultPath)
		else:
			ui.message(_("Error: Add-on user manual is not found"))
	
	def script_displayAudacityGuide (self, gesture):
		stopTaskTimer()
		from languageHandler import curLang
		#docPath=os.path.join(os.path.dirname(__file__), "..\\doc").decode("mbcs")
		docPath = os.path.join(_addonDir , "doc")
		guide = "audacityGuide.html"
		defaultPath = os.path.join(docPath, "en", guide)
		localPath = os.path.join(docPath, curLang, guide)
		if os.path.exists(localPath):
			self.startFile(localPath)
		elif os.path.exists(defaultPath):
			self.startFile(defaultPath)
		else:
			ui.message(_("Error: audacity guide is not found"))


	
	
	def script_test(self, gesture):
		import mouseHandler
		import winUser
		ui.message("Audacity test")
		ao = audacityPackage.objects
		o = ao.lockingTool1Object()



