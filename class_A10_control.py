#!/usr/bin/env python
# coding: utf8
import builtins
import logging
import inspect
from collections import defaultdict
from datetime import datetime
import time
import copy
heat_state_old = -999					## Initialisierung für 1. Lauf
heat_state_ist = -999					## Initialisierung für 1. Lauf
# data_of_this_topic_memory = -999		## Initialisierung für 1. Lauf

class process_control:
	"""
	A class to control various processes
	* Heating ON/OF depending on Month/Day/Time
	* Cooling ON/OF depending on temperature

	Methods
	-------
	do_cooling(topic)
		Returns ON/OF depending on Temperature.
	do_heating()
		Returns ON/OF depending on Month/Day/Time.
	"""

	def __init__(self, config_data):
		self.Control_config=defaultdict(set)
		self.Control_config=config_data["Control"]

		pass

	def check_Temperierung_time(self):
		"""
			Takes the TIME_NOW and determines, if Heating should
			switch ON or OFF

			Parameters
			----------
			chart_nr : int
				Number of chart, chartdata and tablename should be taken
		"""
		# nonlocal data_of_this_topic_memory
		global heat_state_old
		global heat_state_ist
		if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			# print(inspect.stack()[1][1],":",inspect.stack()[1][2],":",inspect.stack()[1][3])
			print ("            ###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> check_Temperierung_time START   ##")


		month_now = int(datetime.today().strftime('%m'))
		day_now = datetime.today().weekday()	# 0 (Mo) - 6 (So)
		time_now = float(datetime.today().strftime('%H.%M'))

		month_set_on=self.Control_config["Temperierung"]["on"]["month"]
		month_set_off=self.Control_config["Temperierung"]["off"]["month"]
		if day_now==5 or day_now==6:	## Sa,So
			time_on=self.Control_config["Temperierung"]["on"]["sa-so_time"]
			time_off=self.Control_config["Temperierung"]["off"]["sa-so_time"]
		else:							## Mo-Fr
			time_on=self.Control_config["Temperierung"]["on"]["mo-fr_time"]
			time_off=self.Control_config["Temperierung"]["off"]["mo-fr_time"]
		if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
			print("                           check_Temperierung_time->Vorgabe: Sollte einschalten (month_set_on) ",month_set_on," ")
			print("                           check_Temperierung_time->Vorgabe: Sollte einschalten (time_on) ",time_on," Uhr (noch nichts ausgewertet)")
			print("                           check_Temperierung_time->info: heat_state_ist=",heat_state_ist," heat_state_old=", heat_state_old)
			print()
		if month_now <= month_set_off or month_now >= month_set_on: ### nur in Wintermonaten
			time_window=0
			if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
				print("                           check_Temperierung_time: Monat, um zu Heizen = OK")
				print()

			if time_on>time_off:		## Startzeit vor Mitternacht / Ende nach Mitternacht
				if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
					print("                           check_Temperierung_time (über Mitternacht): time_on (",time_on,") - time_now (",time_now,") - time_off (",time_off,")")
				if time_now>=time_on or time_now<=time_off:
					if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
						print("                           check_Temperierung_time (über Mitternacht): Ist im Zeitfenster -> Heizen! : time_window=",time_window)
					time_window=1
				else:
					if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
						print("                           check_Temperierung_time (über Mitternacht): Ist NICHT im Zeitfenster -> NICHT Heizen: time_window=",time_window)

			else:						## Startzeit nach Mitternacht / Ende nach Mitternacht
				if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
					print("                           check_Temperierung_time (nach Mitternacht): time_on (",time_on,") - time_now (",time_now,") - time_off (",time_off,")")
				if time_now>=time_on and time_now<=time_off:
					if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
						print("                           check_Temperierung_time (nach Mitternacht): Ist im Zeitfenster -> Heizen! : time_window=",time_window)
					time_window=1
				else:
					if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
						print("                           check_Temperierung_time (nach Mitternacht): Ist NICHT im Zeitfenster -> NICHT Heizen: time_window=",time_window)

			if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
				print("                           check_Temperierung_time: time_window:",time_window)
			if 	time_window == 1 :
				heat_state_ist=1
				if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
					print("                           check_Temperierung_time: time_window OK -> heat_state_ist=1")
			else:
				heat_state_ist=0
				if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
					print("                           check_Temperierung_time:  time_window NOT OK -> heat_state_ist=0")
		else:
			if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
				print("                           check_Temperierung_time: Monat, um zu Heizen = NICHT OK (keine Zeit Überprüfung)")

		if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
			print("                           check_Temperierung_time: heat_state_ist=",heat_state_ist," heat_state_old=", heat_state_old)
		if (heat_state_old == -999):
			heating_out=0
			if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
				print("                           check_Temperierung_time: heat_state_old ist -999!!!")
		else:
			if heat_state_ist > heat_state_old :	# auf ON -> +Flanke
				if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
					print("                           check_Temperierung_time: heating_out =1 -> Einschalten")
				# self.Control_config["Temperierung"]["heat_state_old"]=data_of_this_topic
				# data_of_this_topic_memory=data_of_this_topic
				heating_out=1
			elif heat_state_ist<heat_state_old :	# auf OLD STATE -> -Flanke
				if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
					print("                           check_Temperierung_time: heating_out = -1 -> Ausschalten")
				# topic_out=self.Control_config["Temperierung"]["heat_state_old"]
				# topic_out=int(data_of_this_topic_memory)
				heating_out=-1
			else:			# keine Änderung (in der Zeit)
				if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
					print("                           check_Temperierung_time: heating_out =0  -> Keine Änderung")
				heating_out=0

		heat_state_old = heat_state_ist

		if any(debug_level_str in {"Temperierung"} for debug_level_str in builtins.debug_info_level):
			print("                           check_Temperierung_time: returnvalue heating_out=",heating_out)
			print("            ###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> check_Temperierung_time END   ##")
		return heating_out	## 1 switch ON   // -1 =  switch OFF  // 0 do nothing


class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR
