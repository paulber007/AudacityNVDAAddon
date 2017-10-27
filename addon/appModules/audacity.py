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
import addonHandler
from audacity_docHandler import openDocPath
import utils
from  objects import isPressed

# global timer
GB_Timer = None
addonHandler.initTranslation()

_addonDir = os.path.join(os.path.dirname(__file__), "..").decode("mbcs") # The root of an addon folder
_curAddon = addonHandler.Addon(_addonDir) # Addon instance
_addonSummary = _curAddon.manifest['summary']
_addonVersion = _curAddon.manifest['version']
_addonName = _curAddon.manifest['name']
_scriptCategory = unicode(_addonSummary)
_audacityCommandKeyMsg = _("Reserved: see Audacity command keys")

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
		#self.event_stateChange()
		eventHandler.queueEvent("gainFocus",obj)


	
	script_spaceKey.__doc__ = _audacityCommandKeyMsg
	
		


	
	script_spaceKey.__doc__ = _audacityCommandKeyMsg


class InTracksPanelView(Window):

	_audioChangeGestures = (
		"kb:leftArrow",
		"kb:rightArrow",
		"kb:home",
		"kb:end",
		"kb:shift+a",
		"kb:,",
		"kb:;",
		"kb:shift+,",
		"kb:shift+;"
		)
	_selectionChangeGestures = (
		"kb:shift+home",
		"kb:shift+end",
		"kb:shift+j",
		"kb:shift+k"
		)
	_selectionStartChangeGestures = (
		"kb:shift+leftArrow", 
		"kb:control+shift+rightArrow"
		)
		
	_selectionEndChangeGestures = (
		"kb:shift+rightArrow",
		"kb:control+shift+leftArrow"

		)

		
	def initOverlayClass(self):
		for gesture in self._audioChangeGestures:
			self.bindGesture(gesture, "sayAudioPosition")
		for gesture in self._selectionChangeGestures:
			self.bindGesture(gesture, "saySelection")
		for gesture in self._selectionStartChangeGestures:
			self.bindGesture(gesture, "saySelectionStart")
		for gesture in self._selectionEndChangeGestures:
			self.bindGesture(gesture, "saySelectionEnd")


		self.bindGesture("kb:p", "sayPauseState")
		self.bindGesture("kb:space", "spaceKey")
		self.bindGesture("kb:control+shift+s", "reportSelection")
		self.bindGesture("kb:control+shift+t", "reportAudioPosition")
		self.bindGesture("kb:alt+control+f5", "reportTransportButtonsState")
		
		
	def script_spaceKey(self, gesture):
		gesture.send()
		if not isPressed("play"):
			wx.CallLater(200, utils.sayAudioPosition)
	
	script_spaceKey.__doc__ = _audacityCommandKeyMsg
	
	def script_sayAudioPosition(self, gesture):
		global GB_Timer
		def callback():
			global GB_Timer
			GB_Timer = None
			utils.sayAudioPosition()


		gesture.send()
		if GB_Timer != None:
			GB_Timer.Stop()
			GB_Timer = None
			
		if not isPressed("play")or isPressed("pause"):
			GB_Timer = wx.CallLater(300, callback)
	script_sayAudioPosition.__doc__ = _audacityCommandKeyMsg



			
	def script_saySelectionStart(self, gesture):
		gesture.send()
		if not isPressed("play")or isPressed("pause"):
			wx.CallLater(200, utils.saySelectionStart)
	script_saySelectionStart.__doc__ = _audacityCommandKeyMsg
		
	def script_saySelectionEnd(self, gesture):
		gesture.send()
		if not isPressed("play") or isPressed("pause"):
			wx.CallLater(200, utils.saySelectionEnd)
			
	script_saySelectionEnd.__doc__ = _audacityCommandKeyMsg
	
	def script_saySelection(self, gesture):
		gesture.send()
		if not isPressed("play")or  isPressed("pause"):
			wx.CallLater(200, utils.saySelection)
			
	script_saySelection.__doc__ = _audacityCommandKeyMsg
	def script_sayPauseState(self, gesture):
		gesture.send()
		wx.CallLater(200, utils.sayPauseState)
		
	script_sayPauseState.__doc__ = _audacityCommandKeyMsg

	def script_reportAudioPosition (self, gesture):
		utils.sayAudioPosition()

	script_reportAudioPosition.__doc__ = _("report audio position")
	script_reportAudioPosition.category = _scriptCategory

	def script_reportSelection (self, gesture):		
		utils.saySelection()
	script_reportSelection.__doc__ = _("report start and end of selection")
	script_reportSelection.category = _scriptCategory

	def script_reportTransportButtonsState(self, gesture):
		utils.sayTransportButtonsState()
	script_reportTransportButtonsState.__doc__ = _("report the state of Pause and Play buttons")
	script_reportTransportButtonsState.category = _scriptCategory
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
		if utils.inTracksPanelView(obj):
			clsList.insert(0, InTracksPanelView)
			
		elif obj.role == controlTypes.ROLE_BUTTON:
			clsList.insert(0, Button)

	

	def event_NVDAObject_init(self,obj):
		if obj.windowClassName=="Button" and not obj.role in [controlTypes.ROLE_MENUBAR, controlTypes.ROLE_MENUITEM, controlTypes.ROLE_POPUPMENU]:
			obj.name=winUser.getWindowText(obj.windowHandle).replace('&','')
