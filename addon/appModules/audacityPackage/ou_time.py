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
from time import sleep
def sayTime (sTime):

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

	#ready to say
	if iHours :
		iNoNull = True
		if iHours == 1 :
			ui.message(_("one hour"))
		else:
			ui.message(_("%s hours") %iHours)


	if  iMinutes :
		iNotNull = True
		if iMinutes == 1 :
			ui.message(_("1 minute"))
		else:
			ui.message(_("%s minutes")%iMinutes)


	if iMSeconds :
		iNotNull = True
		if iSeconds :
			if iSeconds == 1 :
				ui.message(_("1 second {0}") .format(iMSeconds))
			else:
				ui.message(_("{0} seconds {1}") .format(iSeconds, iMSeconds))

		else:
			ui.message(_("0 second %s") % iMSeconds)

	else:
		if iSeconds :
			iNotNull = True
			ui.message(_("%s second") %iSeconds)

	if not iNotNull:
		ui.message(_("0 second"))

	sleep(0.5)



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

