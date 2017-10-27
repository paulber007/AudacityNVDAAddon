# -*- coding: UTF-8 -*-

# docHandler: module for managing addons documentation

import os
import languageHandler

#import gui
#import wx
import speech
import api
import time
import addonHandler
addonHandler.initTranslation()
_addonDir = os.path.join(os.path.dirname(__file__), "..").decode("mbcs") # The root of an addon folder
_docFileName = "readme.html" # The name of an addon documentation file


def getDocFolder(addonDir = _addonDir):
	langs = [languageHandler.getLanguage(), "en"]
	for lang in langs:
		docFolder = os.path.join(addonDir, "doc", lang)
		if os.path.isdir(docFolder):
			return docFolder
		if "_" in lang:
			tryLang = lang.split("_")[0]
			docFolder = os.path.join(addonDir, "doc", tryLang)
			if os.path.isdir(docFolder):
				return docFolder
			if tryLang == "en":
				break
		if lang == "en":
			break
	return None

def getDocPath(docFileName=_docFileName):
	docPath = getDocFolder()
	if docPath is not None:
		docFile = os.path.join(docPath, docFileName)
		if os.path.isfile(docFile):
			docPath = docFile

	return docPath

def openDocPath():
	try:
		os.startfile(getDocPath())
		oldSpeechMode = speech.speechMode
		speech.speechMode = speech.speechMode_off
		time.sleep(0.1)
		api.processPendingEvents()
		speech.speechMode = oldSpeechMode
	except WindowsError:
		pass
