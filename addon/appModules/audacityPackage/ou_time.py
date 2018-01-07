# -*- coding: UTF-8 -*-
#audacity/audacityPackage/ou_time.py
# a part of audacity appModule
#Copyright (C) 2015-2017 Paulber19
#This file is covered by the GNU General Public License.
# Released under GPL 2

import ui
import addonHandler
addonHandler.initTranslation()

def formatTime (sTime):
	# to convert a string xxhyymzzs to xx:yy:zz
	#; or xxhyymzz.wwws to xx:yy:zz.www
	sTemp = sTime.lower()
	sTemp =sTemp.replace("h", ":")
	sTemp = sTemp.replace("m", ":")
	sTemp = sTemp.replace("s", "")
	sTemp = sTemp.replace(" ", "")
	return sTemp

def getTimeMessage (sTime):
	iNotNull = False
	lTime = sTime.split(":")
	if len(lTime) == 3:
		iHours = int(lTime[0])
		iMinutes =  int(lTime[1])
		temp =lTime[2].split(".")
		if  len(temp ) == 2:
			iSeconds= int(temp[0])
			iMSeconds= int(temp[1])
		else:
			iSeconds = int(temp[0])
			iMSeconds= 0
	elif len(lTime) == 2:
		iMinutes =  int(lTime[0])
		sTemp =lTime[1].split(".")
		if  len(sTemp) == 2:
			iSeconds= int(sTemp[0])
			iMSeconds= int(sTemp[1])
		else:
			iSeconds = int(sTemp)
			iMSeconds= 0
			
	else:
		if  len(sTime.split("."))== 2 :
			sTemp = sTime.split(".")
			iSeconds= int(sTemp[0])
			iMSeconds= int(sTemp[1])
		else:
			iSeconds = int(sTime)
			iMSeconds= 0
	
	textList = []
	if iHours :
		iNoNull = True
		if iHours == 1 :
			# Translator: a part of message to the user to say one hour
			textList.append(_("one hour"))
		else:
			# a part of message to the user to say  hours
			textList.append( _("%s hours") %iHours)


	if  iMinutes :
		iNotNull = True
		if iMinutes == 1 :
			# Translators: a part of message to the user to say  one minute
			textList.append(_("1 minute"))
		else:
			# Translators: a part of message to the user to say minutes
			textList.append(_("%s minutes")%iMinutes)
	if iMSeconds :
		iNotNull = True
		if iSeconds :
			if iSeconds == 1 :
				# Translators: a part to the user to say one second
				textList.append(_("1 second {0}") .format(iMSeconds))
			else:
				# Translators: a part of message to  the user to say seonds
				textList.append(_("{0} seconds {1}") .format(iSeconds, iMSeconds))
		
		else:
			# Translators: a part of message to the user to say 0 second
			textList.append(_("0 second %s") % iMSeconds)
	
	else:
		if iSeconds :
			iNotNull = True
			# Translators: a part of message to the user to say seconds
			textList.append(_("%s second") %iSeconds)
	
	if not iNotNull:
		# Translators: a part of message to the user to say 0 seconds
		textList.append(_("0 second"))
	return " ".join(textList)


def isNullDuration(sDuration):
	sTemp = sDuration.replace(" ", "")
	sTemp = sTemp.replace(":", "")
	lTemp = sTemp.split(".")
	if len(lTemp) ==2:
		last = lTemp[1]
		sTemp = lTemp[0]
	else:
			last ="0"
			sTemp = lTemp[0]
	
	if (int(sTemp)
		or int(last)):
		return False

	return True

