#appModules/audacityPackage/NVDAStrings.py
# a part of audacity add-on
# Author: paulber19
# Copyright 2016-2017, released under GPL.
#See the file COPYING for more details.


def NVDAString(s):
	""" A simple function to bypass the addon translation system,
	so it can take advantage from the NVDA translations directly.
	Based on implementation made by Alberto Buffolino
	https://github.com/nvaccess/nvda/issues/4652 """
	
	return _(s)

