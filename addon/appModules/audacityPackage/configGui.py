	# audacityPackage/configGui.py
# a part of audacity appModule
# Author: paulber19
# Copyright 2016-2017, released under GPL.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()
from logHandler import log
import wx
import gui
from gui.settingsDialogs import SettingsDialog
from configManager import _addonConfigManager 


class AudacitySettingsDialog(SettingsDialog):
	# Translators: This is the label for the Audacity settings  dialog.
	title = _("Audacity add-on's settings")

	def makeSettings(self, settingsSizer):
		from configManager import _addonConfigManager 
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a checkbox in the FirefoxSettingsDialog.
		labelText= _("Report automaticaly selection's changes")
		self.AutomaticSelectionChangeReportBox =sHelper.addItem(wx.CheckBox(self,wx.NewId(),label=labelText))
		self.AutomaticSelectionChangeReportBox .SetValue(_addonConfigManager .toggleAutomaticSelectionChangeReportOption(False))
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a checkbox in the FirefoxSettingsDialog.
		labelText= _("Use space bar and Enter keys to press button")
		self.UseSpaceBarToPressButtonBox =sHelper.addItem(wx.CheckBox(self,wx.NewId(),label=labelText))
		self.UseSpaceBarToPressButtonBox .SetValue(_addonConfigManager .toggleUseSpaceBarToPressButtonOption(False))		
		# Translators: This is the label for a checkbox in the FirefoxSettingsDialog.
		labelText= _("Report toolbars's name ")
		self.reportToolbarNameOnFocusEnteredBox =sHelper.addItem(wx.CheckBox(self,wx.NewId(),label=labelText))
		self.reportToolbarNameOnFocusEnteredBox  .SetValue(_addonConfigManager .toggleReportToolbarNameOnFocusEnteredOption(False))
		
	def postInit(self):
		self.AutomaticSelectionChangeReportBox.SetFocus()
		
	def saveSettingChanges (self):
		from configManager import _addonConfigManager 
		if self.AutomaticSelectionChangeReportBox.IsChecked() != _addonConfigManager .toggleAutomaticSelectionChangeReportOption(False):
			_addonConfigManager .toggleAutomaticSelectionChangeReportOption(True)
		
		if self.UseSpaceBarToPressButtonBox .IsChecked() != _addonConfigManager .toggleUseSpaceBarToPressButtonOption(False):
			_addonConfigManager .toggleUseSpaceBarToPressButtonOption(True)
		if self.reportToolbarNameOnFocusEnteredBox   .IsChecked() != _addonConfigManager .toggleReportToolbarNameOnFocusEnteredOption(False):
			_addonConfigManager .toggleReportToolbarNameOnFocusEnteredOption(True)
			
	def onOk(self,evt):
		super(AudacitySettingsDialog, self).onOk(evt)
		self.saveSettingChanges()
