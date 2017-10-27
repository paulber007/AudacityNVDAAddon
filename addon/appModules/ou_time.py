import ui
import addonHandler
addonHandler.initTranslation()

def formatTime (sTime):
	# to convert a string xxhyymzzs to xx:yy:zz
	#; or xxhyymzz.wwws to xx:yy:zz.www
	sTemp = sTime.lower()
	sTemp = sTemp# supprimer tous les blancs
	sTemp =sTemp.replace("h", ":")
	sTemp = sTemp.replace("m", ":")
	sTemp = sTemp.replace("s", "")
	return sTemp

def sayTime (sTime):
	iNotNull = False
	time = sTime.split(":")
	if len(time) == 3:
		iHours = int(time[0])
		iMinutes =  int(time[1])
		temp =time[2].split(".")
		if  len(temp ) == 2:
			iSeconds= int(temp[0])
			iMSeconds= int(temp[1])

		else:
			iSeconds = int(sTemp)

	elif len(time) == 2:
		iMinutes =  int(time[0])
		sTemp =time[1].split(".")
		if  len(sTemp) == 2:
			iSeconds= int(sTemp[0])
			iMSeconds= int(sTemp[1])
		else:
			iSeconds = int(sTemp)
			
	else:
		if  len(sTemp.split("."))== 2 :
			sTemp = sTime.split(".")
			iSeconds= int(sTemp[0])
			iMSeconds= int(sTemp[1])
		else:
			iSeconds = int(sTime)

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





