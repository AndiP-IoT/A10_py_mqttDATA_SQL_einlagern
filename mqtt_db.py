#!/usr/bin/env python
# coding: utf8
import os
import builtins
builtins.debug_info_level = {"modulecall","lokalSQL"}
	##  Möglich DEBUG Kürzel
			# modulecall
			# lokalSQL remoteSQL
			# temperierung cooling
			# frost mega2560 doorbell mqtt_publish mqtt
			# print_incomming_data cloud gpio
			# inselWR

import logging
import inspect
import time
import datetime

import term		## https://github.com/gravmatt/py-term

from collections import defaultdict
from time import sleep
import paho.mqtt.client as paho
import A10_mod_ds1820 as mod_DS1820
import A10_mod_mqtt as mod_mqtt
import A10_mod_sensor as mod_sensoren
import A10_mod_sql as mod_sql
import A10_mod_IP as mod_IP
import mod_cursor as mod_cursor

# import class_A10_sensors as sensors
#import modul_A10_sensors
import class_A10_color as textcolors
import class_A10_db as database
import class_A10_control as controller
import class_A10_cloud as iot_cloud
import sys
import subprocess
import copy

# print(dir(iot_cloud))
# exit()

#sys.stderr = open('/media/usbstick/mqtt_db_stderror.log', 'a')
# sys.stderr = open('/home/pi/mqtt_db_stderror.log', 'a')
# logging.basicConfig(handlers=[logging.FileHandler(filename="/media/usbstick/mqtt_db_error.log",
                                                 # encoding='utf-8', mode='a+')],
                    # format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    # datefmt="%F %A %T",
                    # level=logging.INFO)
# logging.basicConfig(handlers=[logging.FileHandler(filename="/home/pi/mqtt_db_error.log",
                                                 # encoding='utf-8', mode='a+')],
                    # format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    # datefmt="%F %A %T",
                    # level=logging.INFO)

# logging.info(__file__+' -> startup process')


####################################################
##             inselWR Settings                        ##
####################################################
inselWR_on_Sol_temp_diff=10	# SOLAR DIFF Panel - Puff_unten
inselWR_on_Sol_soll=-99		# inselWR ein wegen SolarTemp


####################################################
##             MQTT - Broker Credentials          ##
####################################################
mqtt_client_settings=defaultdict(dict)
mqtt_client_settings["username"]="A10"
mqtt_client_settings["password"]="affe123456"
mqtt_client_settings["url"]="10.0.0.200"
# mqtt_client_settings["url"]="127.0.0.1"

####################################################
##              DB (MariaDB) Credentials          ##
####################################################
db_config_data=defaultdict(dict)
db_config_data["user"]="A10"
db_config_data["password"]="qwert"
db_config_data["host"]="127.0.0.1"
# db_config_data["host"]="10.0.0.108"
db_config_data["port"]=3306
db_config_data["database"]="/var/lib/phpliteadmin/a10.db"


####################################################
##                   Sensoren                     ##
##                (mqtt Topics )                  ##
####################################################
# alle mqtt Signale müssen hier definiert werden.
#  TOPIC - SensorSignal
# Wenn kein Maximalwert, sondern der letzt gültige Momentanwert
# in der DB gespeichert werden soll (Pumpen-Ein-Aus, Glocke...)
# so kann dies als
# temp["topic/pfad"]["val_direkt"]=1
# definiert werden
SENSOR_config_array={}
Sensoren_def = {
"WF/DS1820/10EA72E1010800E8" :{"name":"t_Aussen_N"},
"WF/DS1820/106EDEDC01080019" :{"name":"t_WF"},
"Heiz/DS1820/1028B2DC010800EE" :{"name":"Heiz_VL"},
"Heiz/DS1820/1044FCE0020800A5" :{"name":"Puf_unten"},
"Heiz/DS1820/10BA19E102080043" :{"name":"Solar_RL"},
"Heiz/DS1820/10EE2AE10208007B" :{"name":"Puf_sol_VL2"}, #//nicht in DB
"Heiz/DS1820/1019B8E002080037" :{"name":"Puf_heizung"},
"Heiz/DS1820/104BDFDC01080089" :{"name":"Solar_VL"},
"Heiz/DS1820/28C03C480A0000B2" :{"name":"Puf_sol_VL"}, #//nicht in DB
"Heiz/DS1820/28F45C480A000092" :{"name":"WW"},
"Heiz/DS1820/287E71470A000039" :{"name":"Heiz_RL"},
"Heiz/DS1820/286B08480A00008D" :{"name":"Puf_oben"},
"Ofen/DS1820/2878DB470A000005" :{"name":"t_WZ_o"},
"nodered/DS1820/10-000802e0ff5e" :{"name":"t_WZ_t"},
"Ofen/DS1820/280A21480A000072" :{"name":"Ofen_kessel"},
"Ofen/stat/Servo" :{"name":"Ofen_servo"},
"Heiz/DI/Heiz_P_ist" :{"name":"HeizP_ist","val_direkt":1,"datatype":"int"},
"Heiz/DI/Solar_P_ist" :{"name":"SolarP_ist","val_direkt":1,"datatype":"int"},
"Ofen/stat/Kesselpumpe" :{"name":"OfenP_ist","val_direkt":1,"datatype":"int"},
"Heiz/stat/Heiz_HA0" :{"name":"HeizP_HA0_ist","val_direkt":1,"datatype":"int"},
"cmd/NRpython/Heiz_HA0" :{"name":"HeizP_HA0_cmd","val_direkt":1,"datatype":"int"},
"Solar/DS1820/28577495F0013CF3" :{"name":"ThSol_temp1"},
"Solar/DS1820/28B77D95F0013C29" :{"name":"ThSol_temp2"},
"Solar/stat/bootCount" :{"name":"ThSol_bootCount"}, #//nicht in DB



#############   INSEL MPPT
"INSEL/VenusOS/PV_V" :{"name":"PV0_V"},
"INSEL/VenusOS/PV_P" :{"name":"PV0_P"},
"INSEL/VenusOS/Bat_V" :{"name":"MPPT0_V"},#//nicht in DB
"INSEL/VenusOS/Bat_A" :{"name":"MPPT0_I"},#//nicht in DB
# "INSEL/MPPT/IL" :{"name":"MPTT0_IL"},

# "INSEL/MPPT/VPV" :{"name":"PV0_V"},
# "INSEL/MPPT/PPV" :{"name":"PV0_P"},
# "INSEL/MPPT/V" :{"name":"MPPT0_V"},
# "INSEL/MPPT/I" :{"name":"MPPT0_I"},
# "INSEL/MPPT/IL" :{"name":"MPTT0_IL"},
#############   INSEL WR
"online/Victron_0" :{"name":"on_Victron_0","val_direkt":1}, #//nicht in DB
"cmd/NRpython/WR_soll_sol" :{"name":"WR0_soll_Sol","val_direkt":1,"datatype":"int"},
"INSEL/info/WR_soll_PPV" :{"name":"WR0_soll_PPV","val_direkt":1,"datatype":"int"},
"INSEL/info/WR_soll" :{"name":"WR0_soll","val_direkt":1,"datatype":"int"},
"Heiz/DI/WR_ist" :{"name":"WR0_ist","val_direkt":1,"datatype":"int"},

# "INSEL/WR/AC_OUT_V" :{"name":"WR0_AC_OUT_V","factor":100},
# "INSEL/WR/AC_OUT_I" :{"name":"WR0_AC_OUT_I","factor":10},
# "INSEL/WR/AC_OUT_S" :{"name":"WR0_AC_OUT_S","val_direkt":1},
# "INSEL/WR/V" :{"name":"BAT_U_WR","factor":1000},

# "INSEL/current/A0" :{"name":"insel0_A0","factor":1},
# "INSEL/current/A1" :{"name":"insel0_A1","factor":1},
# "INSEL/current/A2" :{"name":"insel0_A2","factor":1},
#############   INSEL BAT
"BMS360/cell/1/V" :{"name":"BMS360_01V","val_direkt":1},
"BMS360/cell/2/V" :{"name":"BMS360_02V","val_direkt":1},
"BMS360/cell/3/V" :{"name":"BMS360_03V","val_direkt":1},
"BMS360/cell/4/V" :{"name":"BMS360_04V","val_direkt":1},
"BMS360/BoV" :{"name":"BMS360_BoV","val_direkt":1},
"BMS360/BuV" :{"name":"BMS360_BuV","val_direkt":1},
"BMS360/V" :{"name":"BMS360_V","val_direkt":1},#//nicht in DB
"BMS360/I" :{"name":"BMS360_I","val_direkt":1},#//nicht in DB
"BMS908/cell/1/V" :{"name":"BMS908_01V","val_direkt":1},#//nicht in DB
"BMS908/cell/2/V" :{"name":"BMS908_02V","val_direkt":1},#//nicht in DB
"BMS908/cell/3/V" :{"name":"BMS908_03V","val_direkt":1},#//nicht in DB
"BMS908/cell/4/V" :{"name":"BMS908_04V","val_direkt":1},#//nicht in DB
"BMS908/BoV" :{"name":"BMS908_BoV","val_direkt":1},#//nicht in DB
"BMS908/BuV" :{"name":"BMS908_BuV","val_direkt":1},#//nicht in DB
"BMS908/V" :{"name":"BMS908_V","val_direkt":1},#//nicht in DB
"BMS908/I" :{"name":"BMS908_I","val_direkt":1},#//nicht in DB
"online/BMS360" :{"name":"on_BMS360","val_direkt":1},#//nicht in DB
"online/BMS908" :{"name":"on_BMS908","val_direkt":1},#//nicht in DB




##############   ESS
# "Heiz/EM24/KWH_TOT" :{"name":"GRID_KWH_TOT","val_direkt":1,"factor":10},
# "Heiz/EM24/KWH_L1" :{"name":"GRID_KWH_L1","val_direkt":1,"factor":10},
# "Heiz/EM24/KWH_L2" :{"name":"GRID_KWH_L2","val_direkt":1,"factor":10},
# "Heiz/EM24/KWH_L3" :{"name":"GRID_KWH_L3","val_direkt":1,"factor":10},
# "N/b827ebd0a895/grid/30/Ac/L1/Power" :{"name":"W_L1","val_direkt":1,"factor":10},
# "N/b827ebd0a895/grid/30/Ac/L2/Power" :{"name":"W_L2","val_direkt":1,"factor":10},
# "N/b827ebd0a895/grid/30/Ac/L3/Power" :{"name":"W_L3","val_direkt":1,"factor":10},
# "NR/EM24/W_L1" :{"name":"GRID_W_L1","val_direkt":1,"factor":10},
# "NR/EM24/W_L2" :{"name":"GRID_W_L2","val_direkt":1,"factor":10},
# "NR/EM24/W_L3" :{"name":"GRID_W_L3","val_direkt":1,"factor":10},
# "Heiz/EM24/W_L1" :{"name":"W_L1","val_direkt":1,"factor":10},
# "Heiz/EM24/W_L2" :{"name":"W_L2","val_direkt":1,"factor":10},
# "Heiz/EM24/W_L3" :{"name":"W_L3","val_direkt":1,"factor":10},
"ESS/VenusOS/MPPT1/PV_P" :{"name":"ESS_MPPT1_PV_P","val_direkt":1},
"ESS/VenusOS/MPPT2/PV_P" :{"name":"ESS_MPPT2_PV_P","val_direkt":1},
"ESS/VenusOS/MPPT3/PV_P" :{"name":"ESS_MPPT3_PV_P","val_direkt":1},
"ESS/VenusOS/MPPTs/Sum_PV_P" :{"name":"ESS_MPPTsum_PV_P"},
"ESS/VenusOS/GRID/L1_P" :{"name":"GRID_P_L1"},
"ESS/VenusOS/GRID/L2_P" :{"name":"GRID_P_L2"},
"ESS/VenusOS/GRID/L3_P" :{"name":"GRID_P_L3"},
"ESS/VenusOS/GRID/kWh_in_today" :{"name":"Grid_kWh_in_today","val_direkt":1},
"ESS/VenusOS/GRID/kWh_in_y" :{"name":"Grid_kWh_in_y","val_direkt":1},




##############   DACH
"uCdach/DS1820/28D5A895F0013C08" :{"name":"t_SolP_09","factor":1},
"uCdach/PT1000_2" :{"name":"t_SolP_02","factor":1},
# "uCdach/DS1820/28555D95F0013C96" :{"name":"t_SolP_02","factor":1},
"uCdach/DS1820/288E0095F0013CD3" :{"name":"t_Dachwim_a","factor":1},
"WF/cmd/Bell" :{"name":"Glocke"},#//nicht in DB

"online/Heiz" :{"name":"on_Heiz","val_direkt":1},#//nicht in DB


}
## "val_direkt"=1 bedeutet,das immer der aktuelle Wert
##		in val_for_chart eingespeichert wird,
## 		nicht der aller höchste im Zeitintervall
SENSOR_config_array["Sensors"]=Sensoren_def
del Sensoren_def

temp={}
# Sensors by Names
for topic in SENSOR_config_array["Sensors"]:
	# print (SENSOR_config_array["Sensors"][topic]["name"])
	temp[SENSOR_config_array["Sensors"][topic]["name"]]=topic
SENSOR_config_array["Sensors_by_Names"]=temp
del temp
# print ([SENSOR_config_array["Sensors_by_Names"]])

# print(SENSOR_config_array["Sensors"]["Heiz/stat/Heiz_HA0"])
# exit()

# temp={}
# temp={1:{"val_for_chart":-100},2:{"val_for_chart":-100},3:{"val_for_chart":-100},4:{"val_for_chart":-100}}


##### https://www.w3schools.com/python/python_dictionaries_nested.asp

# print(SENSOR_config_array["Sensors"]["Heiz/stat/Heiz_HA0"]["chartdata"][1]["val_for_chart"])
# exit()




####################################################
##                 Chart config                   ##
####################################################
# Datensammlung mit verschiedenen Zeitintervallen.
# In diesen Zeitintervallen wird der maximal auftretende
# Wert in der DB in der dazugehörigen Tabelle gespeichert.
# Die Tabellen-ColNames definieren die Signale, welche gespeichert werden.
# Alle anderen werden (für diesen Zeitintervall) verworfen
# Ein anderer Zeitintervall hat andere Table-ColNames und damit andere
# Signale, welche gespeichert werden (können).
# Die Tabellen-ColNames müssen mit den SGRID_P_L1ignalnamen übereinstimmen.

# Die Tabellen in der DB müssen "mit der Hand" erzeugt werden.
# Ein Feld in der Tabelle muss "timestamp" als longInt für die UNIX-time
# definiert werden.
chart_def={
	1:{"DBTable_name":"chartData_1","intervall":35,"savetime":time.time()-30},
	2:{"DBTable_name":"chartData_2","intervall":300,"savetime":time.time()},
	3:{"DBTable_name":"chartData_3","intervall":900,"savetime":time.time()},
	4:{"DBTable_name":"chartData_4","intervall":1800,"savetime":time.time()},
}
SENSOR_config_array["chartDBStuff"]=chart_def
del chart_def

A10_localDB = database.ChartData_DBTables(db_config_data)
##################################################
#######  Check Charts Tabelle in DB    ###########
#  in Database kontrollieren, ob
#  Tabellen für Charts vorhanden sind ->
#  Table-ColNames einlesen und in
#  "SENSOR_config_array" einspeichern
for chart_nr in SENSOR_config_array["chartDBStuff"]:
	col_names=A10_localDB.get_col_headers(SENSOR_config_array["chartDBStuff"][chart_nr]["DBTable_name"])
	# print(col_names)
	## Wenn es für die oben unter ### Chart config ###
	## definierten Charts keine Tabelle gibt, lösche sie
	if not col_names:
		### logging.critical("main-> Es gibt keine DB-Tabelle zum ChartNr=%s",chart_nr)
		del SENSOR_config_array["chartDBStuff"][chart_nr]
	else:
		SENSOR_config_array["chartDBStuff"][chart_nr]["DBTable_ColnamesNames"]=col_names


####################################################
##                CONTROL config                  ##
####################################################
# Einstellungen für verschiedene Steuerungen
# Temperieren: in Wintermonaten vor dem Aufstehen Heizung EIN
# Kühlen     : in Übergangszeit muss eventuell der Pufferspeicher
#              gekühlt werden, indem über das Dachgekühlt wird
temp={}
temp.update({"HeizHA0_merk":-988})	## Startwert
# Temperieren : in Wintermonaten vor dem Aufstehen Heizung EIN
temp["on"]={"month":11}					## November
temp["off"]={"month":3}					## Feber
temp["on"].update({"mo-fr_time":4.50})			#4.30		## 4 Uhr 30 Heizung EIN
temp["off"].update({"mo-fr_time":5.40})			## 5 Uhr 30 Heizung AUS
temp["on"].update({"sa-so_time":6.20})			## 6 Uhr 15 Heizung EIN
temp["off"].update({"sa-so_time":7.30})			## 7 Uhr 30 Heizung AUS
# temp["on"].update({"mo-fr_time":4.50})			#4.30		## 4 Uhr 30 Heizung EIN
# temp["off"].update({"mo-fr_time":5.50})			## 5 Uhr 30 Heizung AUS
# temp["on"].update({"sa-so_time":6.15})			## 6 Uhr 15 Heizung EIN
# temp["off"].update({"sa-so_time":7.30})			## 7 Uhr 30 Heizung AUS
temp["topic"]={"sub":"Heiz/stat/Heiz_HA0"}
temp["topic"].update({"pub":"cmd/NRpython/Heiz_HA0"})
#temp["topic"]["data_type":"int"
SENSOR_config_array.update({"Control":{"Temperierung":temp}})

temp={}
# Kühlen : in Übergangszeit Pufferspeicher kühlen
temp["Grenztemperatur"]={"unten":70}		## unter dieser Temp. Kühlung aus
temp["Grenztemperatur"].update({"oben":90})	## über dieser Temp. Kühlung ein
SENSOR_config_array["Control"]["Kuehlung"]=temp

##--------------------------------------------------------------------##
##--------------------------------------------------------------------##
##       unterhalb von hier ist normalerweise nichts zu ändern        ##
########################################################################

####   globale Variable ################################################
SENSOR_NaN=-9999
print ("Let's go")
########################################################################



####################################################
##                   Translate                    ##
####################################################
# Bringt das MQTT-Topic keinen 'float' Wert mit
#      (=konvertierbarer String)
# so kann eine 'Translate' Tabelle helfen
# ALLE Topics mit "ON" werden dann z.B. in "1" übersetzt.
temp={}
temp["translate"]={"ON":1,"OFF":0,"digON":1,"digOFF":0,"on hand":2}
SENSOR_config_array["config_sonstiges"]=temp



mod_sensoren.prepare_sensor_array(SENSOR_config_array)


# A10_sensors_class = sensors.deal_with_sensorData(SENSOR_config_array)
Control = controller.process_control(SENSOR_config_array)
IoTCloud = iot_cloud.iot_cloud()
############ Sensor Class definieren ENDE



####################################################
##           MQTT Verbindung aufbauen             ##
####################################################
mqtt_client = paho.Client(client_id="",clean_session=True,userdata=SENSOR_config_array,protocol=paho.MQTTv311,transport="tcp")
mqtt_client.on_connect = mod_mqtt.on_mqtt_connect
mqtt_client.on_message = mod_mqtt.on_mqtt_message_arrive 		##  callback !!!
mqtt_client.username_pw_set(username=mqtt_client_settings["username"],password=mqtt_client_settings["password"])
print("Startup -> MQTT Connecting...")
mqtt_client.connect(mqtt_client_settings["url"],1883)
print("Startup -> MQTT Connecting...OK")
mqtt_client.loop_start()
##           MQTT Verbindung aufbauen END        ##

# logging.basicConfig(filename='mqtt_logging.log', encoding='utf-8', level=###logging.debug()
# logging.basicConfig(format='%(asctime)s %(message)s')
# logging.basicConfig(handlers=[logging.FileHandler(filename="/media/usbstick/mqtt_db_error.log",
                                                 # encoding='utf-8', mode='a+')],
                    # format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    # datefmt="%F %A %T",
                    # level=logging.INFO)


# ###logging.debug(('This message should go to the log file')
###logging.info('mqtt Python just starts')
# logging.warning('And this, too')
# logging.error('And non-ASCII stuff, too, like Øresund and Malmö')


# SENSOR_config_array["Sensors"]=A10_sensors_class.prepare_sensor_array()
####################################################
####################################################
##                 HAUPTPROGRAMM                  ##
####################################################
####################################################
old_10seconds=time.time()
###logging.info(__file__+' -> startup process -> enter while 1==1')
SolP_Intervallstart_time = 0
SolP_frost_run=False
SolP_timeset=-999				## First run
# HeizP_vor_Temperierung=-999		## First run
t_WZ_t=0.0
roundcount=0

mod_IP.get_IP(mqtt_client)
# ipv4 = os.popen('ip addr show eth0 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip()
# print("Startup IPV4=",ipv4)
# mod_mqtt.mqtt_publish(mqtt_client,"NRpython/info/ip",ipv4,"")
mod_mqtt.mqtt_publish(mqtt_client,"info/startup/NRpython","1","")

while 1==1 :

	#### Textteile für Bildschirmausgabe
	temp[0]="          noch "
	temp[1]=""
	temp[2]=" Sekunden bis SQL Speicherung"

	#####################################################
	##           für alle CHART Definitionen           ##
	#####################################################
	# for chart_nr in A10_sensors_class.chartDBStuff:
	for chart_nr in SENSOR_config_array["chartDBStuff"]:
		### hole die UNIX-Time vom letzten SQL-Save
		old_seconds_impuls=SENSOR_config_array["chartDBStuff"][chart_nr]["savetime"]

		### in welchem Abstand sollen die CHART-Data SQL-Save werden?
		time_trigger=SENSOR_config_array["chartDBStuff"][chart_nr]["intervall"]
		temp[1]=temp[1]+" / "+str(int(old_seconds_impuls-time.time()+time_trigger))

		### Wenn die Chart-"Wartezeit" abgelaufen ist, speichere
		###    den Zeitpunkt als UNIX-Time für nächsten Intervall
		###    Erzeuge dann mit SensorClass den SQL String für die
		###    Signale in passender Tabelle   laut ChartNr
		if time.time()- old_seconds_impuls > time_trigger :
			###logging.info('running DB save impuls')
			SENSOR_config_array["chartDBStuff"][chart_nr]["savetime"]=time.time()
			DBtable=SENSOR_config_array["chartDBStuff"][chart_nr]["DBTable_name"]

			if any(debug_level_str in {"lokalSQL","remoteSQL","modulecall",""} for debug_level_str in builtins.debug_info_level):
				print()
				print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+" in  MAIN while -> cloud_send_data SQL for CHART #"+str(chart_nr)+" START")
			ret=mod_sql.make_SQLstring(chart_nr,SENSOR_config_array)
			A10_localDB.execute_sql(ret["sql_string"])
			##IoTCloud.cloud_send_data(ret)
			if any(debug_level_str in {"lokalSQL","remoteSQL","modulecall",""} for debug_level_str in builtins.debug_info_level):
				print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+" in  MAIN while -> cloud_send_data SQL for CHART END")
				print ()


	######################################################
	######          RestZeit Ausgabe         #############
	######################################################
	# # # # # term_width=os.get_terminal_size().columns
	# # # # # curs_x, curs_y = mod_cursor.getcursorpos()
	# # # # # spacetring=" "
	# # # # # for x in range(1, term_width, 1):
		# # # # # spacetring = spacetring+" "
	# # # # # curs_x  = curs_x -1
	# # # # # print("\033[{0};{1}H{2}".format(0, 0,spacetring,end="\r",flush=True))
	# # # # # term.clear()
	# # # # # # print('{0:>30} {1:<30} '.format(temp[0],temp[1])+temp[2]+"                    MAIN->"+str(inspect.currentframe().f_lineno), end='\r'
	# # # # # # print("                                                                                                                                     ")
	# # # # # print('{0:>30} {1:<30} '.format(temp[0],temp[1])+temp[2]+"                    MAIN->"+str(inspect.currentframe().f_lineno)+"                                                    ")
	# # # # # print(spacetring)
	# # # # # #print('\033[{0};{1}{2:>30} {3:<30} '.format(0,0,temp[0],temp[1])+temp[2]+"                    MAIN->"+str(inspect.currentframe().f_lineno), end='\r')
	# # # # # # print("\033[{0};{1}H{2}".format(0, 0, "                  Hello world                        "))
	# # # # # print("\033[{0};{1}H{2}".format(curs_x, curs_y," ",end="\r",flush=True))
	# # # # # # print(f"Cursor x: {curs_x}, y: {curs_y}")



	term.saveCursor()
	term.homePos()
	# print("\033[{0};{1}H{2}".format(0, 0," ",end="\r"))
	term.clearLine()
	print(" ")
	term.clearLine()
	print('\033[91m {0:>30} {1:<30} '.format(temp[0],temp[1])+temp[2]+"                    MAIN->"+str(inspect.currentframe().f_lineno))
	term.clearLine()
	term.restoreCursor()


	###############################
	####    10Sekunden Impuls  ####
	###############################
	if time.time()- old_10seconds > 10 :
		roundcount=roundcount+1
		mod_IP.get_IP(mqtt_client)
		print ("#####"+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> 10sec Impuls   ##")
		# ipv4 = os.popen('ip addr show eth0 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip()
		# # print(ipv4)
		# mod_mqtt.mqtt_publish(mqtt_client,"NRpython/info/ip",ipv4,"")
		mod_mqtt.mqtt_publish(mqtt_client,"info/online/NRpython",roundcount,"")

		###############################
		####    DS1820 on GPIO     ####
		debug_str="gpio"
		if any(debug_level_str in {debug_str,"modulecall",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print()
			print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> DS1820 on GPIO START   ##")
		try:
			t_WZ_t=mod_DS1820.get_gpio_ds1820()
		except:
			t_WZ_t="NC"

		mod_mqtt.mqtt_publish(mqtt_client,"NRpython/DS1820/10-000802e0ff5e",t_WZ_t,"")
		old_10seconds=time.time()
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print ("###############  -> DS1820 on GPIO END   ##")
			print()
		####   DS1820 on GPIO END     ####
		##################################

		###############################
		####      FROST Schutz    #####
		debug_str="frost"
		if any(debug_level_str in {debug_str,"modulecall",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print()
			print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> Frost Schutz START   ##")
		Frostschutz_laufzeit=8
		Frostschutz_Grenztemp=-10.0
		t_SolP_09=mod_sensoren.get_one_sensor("uCdach/DS1820/288E0095F0013CD3",SENSOR_config_array)  # Dach Wimmerl Außentemperatur

		if (t_SolP_09 < Frostschutz_Grenztemp) and (t_SolP_09 != SENSOR_NaN):
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print("       FROSTSCHUZ!!!", \
						"     SolP_frost_run =",SolP_frost_run, \
						"     aktuelle Minute=", datetime.datetime.now().minute, \
						"     aktuelle Dach Temp=",t_SolP_09, \
						"     Frostschutz_Grenztemp=",Frostschutz_Grenztemp, \
						)
			if (datetime.datetime.now().minute in {11, 30}) and (SolP_frost_run==False):
				if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
					print("                          Solarpumpe EIN",datetime.datetime.now())
				SolP_timeset = datetime.datetime.now().minute
				# mod_mqtt.mqtt_publish(mqtt_client,"cmd/NRpython/SolarP_override",1,"int")
				SolP_frost_run=True
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print ("                              ", \
					"gestartet Minute : ",SolP_timeset, \
					"läuft noch : ",SolP_timeset-datetime.datetime.now().minute+Frostschutz_laufzeit," Minuten" \
					)
			if ((datetime.datetime.now().minute - SolP_timeset) > Frostschutz_laufzeit) and (SolP_frost_run==True):
				mod_mqtt.mqtt_publish(mqtt_client,"cmd/NRpython/SolarP_override",0,"int")
				SolP_frost_run=False
				if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
					print(" FROSTSCHUTZ Zeitende -> SolPumpe AUS")
		elif (SolP_frost_run==True) and (t_SolP_09 != SENSOR_NaN) :
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print(" Kein FROSTSCHUTZ -> SolPumpe AUS")
			mod_mqtt.mqtt_publish(mqtt_client,"cmd/NRpython/SolarP_override",0,"int")
			SolP_frost_run=False
		else :
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print("       frostschutz called", \
						"     aktuelle Dach Temp=",t_SolP_09, \
						"     Frostschutz_Grenztemp=",Frostschutz_Grenztemp, \
						)
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print ("############### -> Frost Schutz END   ##")
			print()
		####   FROST Schutz END   #####
		###############################


		####################################
		####     cooling (Schutz)       ####
		####     Puffer zu heiß+H0A(C)  ####
		SolP_cooling_run=False
		debug_str="cooling",
		if any(debug_level_str in {debug_str,"modulecall",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print()
			print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> cooling Schutz START   ##")

		topic=SENSOR_config_array["Control"]["Temperierung"]["topic"]["pub"]
		HeizHA0_ist = SENSOR_config_array["Sensors"]["Heiz/stat/Heiz_HA0"]["values"]["val_aktuell"] ## currend state
		if (HeizHA0_ist==2):
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
				# print(inspect.stack()[1][1],":",inspect.stack()[1][2],":",inspect.stack()[1][3])
				print("                                     :"+str(inspect.currentframe().f_lineno)+"  -> 'HeizHA0_ist=COOLING'!!!!!!")
				# logging.info(__file__+' -> main got value-> SolarP override'+mqtt_message)
			if (datetime.datetime.now().hour<5):
				## Zwischen 0 Uhr und 5 wird gekühlt, wenn in NR eingestellt
				SolP_cooling_run=True
				if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
					##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
					# print(inspect.stack()[1][1],":",inspect.stack()[1][2],":",inspect.stack()[1][3])
					print("                                     :"+str(inspect.currentframe().f_lineno)+"  -> SolarP override durch 'HeizHA0_ist=COOLING'")
					# logging.info(__file__+' -> main got value-> SolarP override'+mqtt_message)
					print("                                     :"+str(inspect.currentframe().f_lineno)+"  -> Uhrzeit:hour="+str(datetime.datetime.now().hour))
			else:
				SolP_cooling_run=False
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print ("############### -> cooling Schutz END   ##")
			print()
		####   cooling (Schutz) END   ####
		##################################


		####################################
		####     SolarP override        ####
		####  fetch von Cloud Bedienung ####
		SolP_cloud_run=False
		debug_str="cloud"
		if any(debug_level_str in {debug_str,"modulecall",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print()
			print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> SolarP override (cloud) START   ##")
		mqtt_message=IoTCloud.fetch_cloud_data("SolarP_override")
		if isinstance(mqtt_message, int):   ## The isinstance() function returns True if the specified object is of the specified type, otherwise False.
			if (mqtt_message!=-999):
				SolP_cloud_run=True
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
				# print(inspect.stack()[1][1],":",inspect.stack()[1][2],":",inspect.stack()[1][3])
				print("                                     :"+str(inspect.currentframe().f_lineno)+"  -> SolarP override fetch="+mqtt_message)
				print("                                     :"+str(inspect.currentframe().f_lineno)+"  -> SolarP override durch Cloud Bedienung")
				# logging.info(__file__+' -> main got value-> SolarP override'+mqtt_message)


		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print ("############### -> SolarP override (cloud) END   ##")
			print()
		####     SolarP override        ####
		####  fetch von Cloud Bedienung ####
		####     END                    ####
		####################################

		###############################
		####   SolarP override    #####
		debug_str="SolarP"
		if any(debug_level_str in {debug_str,"modulecall",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print()
			print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> SolarP override START   ##")
		if (SolP_frost_run) or (SolP_cooling_run) or (SolP_cloud_run):
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print("                                     :"+str(inspect.currentframe().f_lineno)+"  -> SolarP override ON --> MQTT PUB")
			mod_mqtt.mqtt_publish(mqtt_client,"cmd/NRpython/SolarP_override",1,"int")
		else:
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print("                                     :"+str(inspect.currentframe().f_lineno)+"  -> SolarP override OFF --> MQTT PUB")
			mod_mqtt.mqtt_publish(mqtt_client,"cmd/NRpython/SolarP_override",0,"int")
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			print ("############### -> SolarP override END    ####")
			print()
		####   SolarP override END   #####
		##################################


		##################################
		####   Temperierung (Bad/WZ)  ####
		####          HeizP run       ####
		debug_str="temperierung"
		if any(debug_level_str in {debug_str,"modulecall",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print()
			print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> Temperierung START   ##")

		topic=SENSOR_config_array["Control"]["Temperierung"]["topic"]["pub"]


		### Zwischenspeichern des momentanen Status HA0 der Heizungspumpe, um nach Zeitablauf wieder herzustellen
		HeizHA0_ist = SENSOR_config_array["Sensors"]["Heiz/stat/Heiz_HA0"]["values"]["val_aktuell"] ## currend state
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			print ("            "+__file__+":"+str(inspect.currentframe().f_lineno)+'  Temperierung : (topic=',topic,' Sensor...["Heiz/stat/Heiz_HA0"]["values"][val_aktuell])  HeizHA0_ist =',HeizHA0_ist)

		##### if we have a valid 'HeizHA0_ist' (=MQTT->Heiz/stat/Heiz_HA0) and we did not already remember
		##		remember it
		##			HeizHA0_merk = -988  -> Startwert bei Python Neustart
		##			HeizHA0_ist  = -111  -> Startwert für MQTT-Variablen, wenn noch kein Wert empfangen wurde
		## 			siehe A10_mod_sensor.prepare_sensor_array()
		if HeizHA0_ist == -111:
			###		noch kein gültiger Wert via MQTT, dann darf nichts passieren
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print ("            "+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> noch kein gültiges Datum vom mqtt 'HeizP_HA0_ist'-> warten")
		else:
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print ("            "+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> mqtt 'HeizP_HA0_ist' gültig-> -> Check Zeitfenster")
			##		es gibt einen gültigen MQTT Wert
			##		check time, date and do the 'HeizHA0_cmd'
			Temperierung_cmd=Control.check_Temperierung_time()		## ist die Zeit für Temperierung passend?
			## Rückgabe Wert: 1 EIN / -1 AUS / 0 nix tun
			HeizHA0_cmd = SENSOR_config_array["Control"]["Temperierung"]["HeizHA0_merk"]
			mod_mqtt.mqtt_publish(mqtt_client,"info/NRpython/HeizP_Temperierung/ge","merkt:"+str(HeizHA0_cmd),"")

			# topic=SENSOR_config_array["Control"]["Temperierung"]["topic"]["pub"]
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print ("            "+__file__+":"+str(inspect.currentframe().f_lineno)+"  ->Zeitfenster check end->Temperierung_cmd=",Temperierung_cmd," ( EIN=1/AUS=-1/nix tun=0?)")
			if Temperierung_cmd == 1 :	## Temperierung Einschalten
				SENSOR_config_array["Control"]["Temperierung"]["HeizHA0_merk"]=HeizHA0_ist
				HeizHA0_cmd = "1"		## Temperierung Einschalten = HAND
				mod_mqtt.mqtt_publish(mqtt_client,topic,HeizHA0_cmd,"")
				mod_mqtt.mqtt_publish(mqtt_client,"info/NRpython/HeizP_Temperierung/1","Temp_ein:"+str(HeizHA0_cmd),"")
				if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
					print("            "+__file__+":"+str(inspect.currentframe().f_lineno)+"  Temperierung: Heizfenster gekommen (Flanke+) => HeizP einschalten (Temperier Befehl =", \
										Temperierung_cmd,") ", \
										" es wird via MQTT HeizHA0_cmd geschickt. ",topic," ",HeizHA0_cmd)
			if Temperierung_cmd == -1 :	## Temperierung Ausschalten = gemerkter Zustand herstellen
				if SENSOR_config_array["Control"]["Temperierung"]["HeizHA0_merk"]!=988: ## = Startwert bei Python Neustart -> nix retourschalten
					HeizHA0_cmd = SENSOR_config_array["Control"]["Temperierung"]["HeizHA0_merk"]
					mod_mqtt.mqtt_publish(mqtt_client,topic,HeizHA0_cmd,"")
					mod_mqtt.mqtt_publish(mqtt_client,"info/NRpython/HeizP_Temperierung/-1","Temp_aus->alt="+str(HeizHA0_cmd),"")
					if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
						print("            "+__file__+":"+str(inspect.currentframe().f_lineno)+"  Temperierung: Heizfenster gegangen (Flanke-) => retour schalten (Temperier Befehl =",\
										Temperierung_cmd,") ", \
									" es wird via MQTT HeizHA0_cmd retour (Zustand vor Zeitfenster) gesetzt. ",topic," ",HeizHA0_cmd)
			if Temperierung_cmd == 0 :	## Temperierung nixtun
				mod_mqtt.mqtt_publish(mqtt_client,"info/NRpython/HeizP_Temperierung/0","Temp_nix tun","")
				if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
					print("            "+__file__+":"+str(inspect.currentframe().f_lineno)+"  Temperierung: keine Änderung -> (Temperier Befehl =", \
										Temperierung_cmd,") ", \
									" es wird nix gemacht")

		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			print ("############### -> Temperierung END    ####")
			print()
		####     Temperierung END     ####
		##################################

		##################################
		####      inselWR ein         ####
		debug_str="inselWR"
		if any(debug_level_str in {debug_str,"modulecall",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print()
			print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  inselWR ein START ##")
		topic=SENSOR_config_array["Sensors_by_Names"]["t_SolP_02"]
		t_SolP_02 = SENSOR_config_array["Sensors"][topic]["values"]["val_aktuell"]
		topic=SENSOR_config_array["Sensors_by_Names"]["Puf_unten"]
		Puf_unten = SENSOR_config_array["Sensors"][topic]["values"]["val_aktuell"]
		# print ("t_SolP_02",t_SolP_02)
		# print ("Puf_unten",Puf_unten)
		if t_SolP_02> -20 and Puf_unten> -20:
			print ("                         "+__file__+":"+str(inspect.currentframe().f_lineno)+" --> inselWR_soll_sol Startbedingungen OK panel & puffer data ok")

			if t_SolP_02>Puf_unten+inselWR_on_Sol_temp_diff:
				print ("                         "+__file__+":"+str(inspect.currentframe().f_lineno)+" --> inselWR_soll_sol t_SolP_02>Puf_unten+inselWR_on_Sol_temp_diff")
				mod_mqtt.mqtt_publish(mqtt_client,"cmd/NRpython/WR_soll_sol",1,"int")
				inselWR_on_Sol_soll=True;
			if t_SolP_02<=Puf_unten:
				print ("                         "+__file__+":"+str(inspect.currentframe().f_lineno)+" --> t_SolP_02<=Puf_unten")
				mod_mqtt.mqtt_publish(mqtt_client,"cmd/NRpython/WR_soll_sol",0,"int")
				inselWR_on_Sol_soll=False
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print()
			print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  WR ein END ##")
		####      WR ein END          ####
		##################################



		##################################
		####        IP Address        ####
		debug_str="IP"
		if any(debug_level_str in {debug_str,"modulecall",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print()
			print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  IP START ##")
		# for IP_to_ping in ["10.0.0.12","10.0.0.13","10.0.0.112","10.0.0.113","10.0.0.35","10.0.0.37","10.0.0.99"]:
			# print("PING check ",IP_to_ping)
			# IP_connected=mod_IP.ping(IP_to_ping)

			# if IP_connected=="CONNECTED":
				# print("PING ",IP_to_ping," OK")
				# mod_mqtt.mqtt_publish(mqtt_client,"info/IP_connected",IP_to_ping,"")
			# else:
				# print("PING ",IP_to_ping," fail")
				# mod_mqtt.mqtt_publish(mqtt_client,"info/IP_no",IP_to_ping,"")

		# print("PING",mod_IP.ping("10.0.0.12"))
		# print("PING",mod_IP.ping("10.0.0.13"))
		# print("PING",mod_IP.ping("10.0.0.112"))
		# print("PING",mod_IP.ping("10.0.0.113"))
		# print("PING",mod_IP.ping("10.0.0.37"))
		# print("PING",mod_IP.ping("10.0.0.35"))
		# print("PING",mod_IP.ping("10.0.0.99"))
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print()
			print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  IP END ##")
		####      IP Address END      ####
		##################################


	####    10Sekunden Impuls  END    ####
	######################################
	topic=SENSOR_config_array["Sensors_by_Names"]["WR0_soll"]
	# print("main-> WR_soll Solar temp-diff",inselWR_on_Sol_soll)
	# print("main-> WR_soll ",SENSOR_config_array["Sensors"][topic]["values"]["val_aktuell"])
	topic=SENSOR_config_array["Sensors_by_Names"]["WR0_ist"]
	# print("main-> WR_ist ",SENSOR_config_array["Sensors"][topic]["values"]["val_aktuell"])

	topic=SENSOR_config_array["Sensors_by_Names"]["t_SolP_02"]
	t_SolP_02 = SENSOR_config_array["Sensors"][topic]["values"]["val_aktuell"]
	topic=SENSOR_config_array["Sensors_by_Names"]["Puf_unten"]
	Puf_unten = SENSOR_config_array["Sensors"][topic]["values"]["val_aktuell"]
	# print ("t_SolP_02",t_SolP_02)
	# print ("Puf_unten",Puf_unten)

	sleep(1) # Stop maxing out CPU
	#print ("\n------ ca 1 Sekunde\n")
exit()

