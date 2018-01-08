#appModules/audacityPackage/informationsBox.py
# a part of audacity add-on
# Author: paulber19
# Copyright 2016-2017, released under GPL.
#See the file COPYING for more details.


import addonHandler
addonHandler.initTranslation()
import api
import speech
import wx
import time
from gui import guiHelper, mainFrame
from NVDAStrings import NVDAString
from utils import isOpened
import os


class InformationDialog(wx.Dialog):
	_instance = None
	# Translators: this is the default title of Information dialog
	title = _("%s - Informations")
	def __new__(cls, *args, **kwargs):
		if InformationDialog._instance is not None:
			return InformationDialog._instance
		obj = super(InformationDialog, cls).__new__(cls, *args, **kwargs)
		return obj
	def __del__(self):
		InformationDialog._instance = None
	
	def __init__(self, parent, informationLabel = "", information= "" ):
		if InformationDialog._instance is not None:
			return
		
		InformationDialog._instance = self
		addonDir = os.path.join(os.path.dirname(__file__), "..\..").decode("mbcs") # The root of an addon folder
		curAddon = addonHandler.Addon(addonDir) # Addon instance
		summary = curAddon.manifest["summary"]
		title = self.title%summary
		super(InformationDialog, self).__init__(parent, wx.ID_ANY,title)
		self.informationLabel = informationLabel
		self.information = information
		self.doGui()
		self.Center(wx.BOTH | wx.CENTER_ON_SCREEN)
		self.Show()     
	
	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the text control
		tcLabel =sHelper.addItem(wx.StaticText(self, label=self.informationLabel))
		self.tc = sHelper.addItem(wx.TextCtrl(self, id = wx.ID_ANY,style=wx.TE_MULTILINE | wx.TE_READONLY|wx.TE_RICH, size = (1000, 600)))
		self.tc.AppendText(self.information)
		self.tc.SetInsertionPoint(0)
		# the buttons
		bHelper = sHelper.addDialogDismissButtons(guiHelper.ButtonHelper(wx.HORIZONTAL))
		# Translators: label of copy to clipboard button
		copyToClipboardButton = bHelper.addButton(self, id = wx.ID_ANY, label = _("Co&py to Clipboard"))
		closeButton= bHelper.addButton(self, id = wx.ID_CLOSE, label = NVDAString("&Close"))
		mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# events
		copyToClipboardButton.Bind(wx.EVT_BUTTON,self.onCopyToClipboardButton)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.tc.SetFocus()
		self.SetEscapeId(wx.ID_CLOSE)
	
	def onCopyToClipboardButton(self, event):
		if api.copyToClip(self.information):
			# Translators: message to the user when the information has been copied to clipboard
			text = _("Copied")
			speech.speakMessage(text)
			time.sleep(0.8)
			self.Close()
		else:
			# Translators: message to the user when the information cannot be copied to clipboard
			text =_("Error, the information cannot be copied to the clipboard")
			speech.speakMessage(text)
			
	@classmethod
	def run(cls, parent, informationLabel, information):
		if isOpened(InformationDialog):
			return
		
		if not parent:
			mainFrame.prePopup()
		InformationDialog(parent or mainFrame, informationLabel, information)
		if not parent:
			mainFrame.postPopup()
		
informationsBox = InformationDialog.run