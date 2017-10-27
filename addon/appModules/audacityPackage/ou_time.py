#audacity/audacityPackage/ou_time.py
#Copyright (C) 2015-2017 Paulber19
#This file is covered by the GNU General Public License.
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
			textList.append(_("one hour"))
		else:
			textList.append( _("%s hours") %iHours)


	if  iMinutes :
		iNotNull = True
		if iMinutes == 1 :
			textList.append(_("1 minute"))
		else:
			textList.append(_("%s minutes")%iMinutes)
	if iMSeconds :
		iNotNull = True
		if iSeconds :
			if iSeconds == 1 :
				textList.append(_("1 second {0}") .format(iMSeconds))
			else:
				textList.append(_("{0} seconds {1}") .format(iSeconds, iMSeconds))
		
		else:
			textList.append(_("0 second %s") % iMSeconds)
	
	else:
		if iSeconds :
			iNotNull = True
			textList.append(_("%s second") %iSeconds)
	
	if not iNotNull:
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

