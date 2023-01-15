#!/usr/bin/env python
# coding: utf8
import builtins
builtins.debug_info_level = {"Temperierung"}
# builtins.debug_info_level = {"Temperierung","",""}
	##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud gpio

import logging
import inspect
import time
import datetime
from collections import defaultdict
from time import sleep
import paho.mqtt.client as paho
import A10_mod_ds1820 as mod_DS1820
import A10_mod_mqtt as mod_mqtt
import A10_mod_sensor as mod_sensoren
import A10_mod_sql as mod_sql

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
db_config_data["database"]="A10"


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
"Heiz/DS1820/10EE2AE10208007B" :{"name":"Puf_sol_VL2"},
"Heiz/DS1820/1019B8E002080037" :{"name":"Puf_heizung"},
"Heiz/DS1820/104BDFDC01080089" :{"name":"Solar_VL"},
"Heiz/DS1820/28C03C480A0000B2" :{"name":"Puf_sol_VL"},
"Heiz/DS1820/28F45C480A000092" :{"name":"WW"},
"Heiz/DS1820/287E71470A000039" :{"name":"Heiz_RL"},
"Heiz/DS1820/286B08480A00008D" :{"name":"Puf_oben"},
"Ofen/DS1820/2878DB470A000005" :{"name":"t_WZ_o"},
"nodered/DS1820/10-000802e0ff5e" :{"name":"t_WZ_t"},
"Ofen/DS1820/280A21480A000072" :{"name":"Ofen_kessel"},
"Ofen/stat/Servo" :{"name":"Ofen_servo"},
"Heiz/DI/Heiz_P_ist" :{"name":"Heiz_P_ist","val_direkt":1,"datatype":"int"},
"Heiz/DI/Solar_P_ist" :{"name":"SolarP_ist","val_direkt":1,"datatype":"int"},
"Ofen/stat/Kesselpumpe" :{"name":"OfenP_ist","val_direkt":1,"datatype":"int"},
"Heiz/stat/Heiz_HA0" :{"name":"HeizP_HA0_ist","val_direkt":1,"datatype":"int"},
"Heiz/cmd/Heiz_HA0" :{"name":"HeizP_HA0_cmd","val_direkt":1,"datatype":"int"},
"Solar/DS1820/28577495F0013CF3" :{"name":"ThSol_temp1"},
"Solar/DS1820/28B77D95F0013C29" :{"name":"ThSol_temp2"},
"Solar/stat/bootCount" :{"name":"ThSol_bootCount"},
"Power_Ke/MPPT/VPV" :{"name":"PV_V","factor":1000},
"Power_Ke/MPPT/PPV" :{"name":"PV_P"},
# "Power_Ke/MPPT/PPV" :{"factor":1000},
"Power_Ke/MPPT/V" :{"name":"BAT_U","factor":1000},
"Power_Ke/MPPT/I" :{"name":"BAT_I","factor":1000},
"Power_Ke/MPPT/IL" :{"name":"MPTT_IL","factor":1000},
"Power_Ke/WR/AC_OUT_V" :{"name":"AC_OUT_V","factor":100},
"Power_Ke/WR/AC_OUT_I" :{"name":"AC_OUT_I","factor":10},
"Power_Ke/WR/AC_OUT_S" :{"name":"AC_OUT_S"},
"Power_Ke/WR/V" :{"name":"BAT_U_WR","factor":1000},
"Power_Ke/current/A0" :{"name":"A0","factor":1},
"Power_Ke/current/A1" :{"name":"A1","factor":1},
"Power_Ke/current/A2" :{"name":"A2","factor":1},
"Heiz/EM24/KWH_TOT" :{"name":"KWH_TOT","val_direkt":1,"factor":10},
"Heiz/EM24/KWH_L1" :{"name":"KWH_L1","val_direkt":1,"factor":10},
"Heiz/EM24/KWH_L2" :{"name":"KWH_L2","val_direkt":1,"factor":10},
"Heiz/EM24/KWH_L3" :{"name":"KWH_L3","val_direkt":1,"factor":10},
"Heiz/EM24/W_L1" :{"name":"W_L1","val_direkt":1,"factor":10},
"Heiz/EM24/W_L2" :{"name":"W_L2","val_direkt":1,"factor":10},
"Heiz/EM24/W_L3" :{"name":"W_L3","val_direkt":1,"factor":10},
"uCdach/DS1820/28D5A895F0013C08" :{"name":"t_SolP_09","factor":1},
"uCdach/DS1820/288E0095F0013CD3" :{"name":"t_Dachwim_a","factor":1},
"WF/cmd/Bell" :{"name":"Glocke"},
}
## "val_direkt"=1 bedeutet,das immer der aktuelle Wert
##		in val_for_chart eingespeichert wird,
## 		nicht der aller höchste im Zeitintervall
SENSOR_config_array["Sensors"]=Sensoren_def
del Sensoren_def

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
# Die Tabellen-ColNames müssen mit den Signalnamen übereinstimmen.

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
temp.update({"HeizHA0_merk":-988})
# Temperieren : in Wintermonaten vor dem Aufstehen Heizung EIN
temp["on"]={"month":11}					## November
temp["off"]={"month":3}					## Feber
temp["on"].update({"mo-fr_time":4.30})			#4.30		## 4 Uhr 30 Heizung EIN
temp["off"].update({"mo-fr_time":5.30})			## 5 Uhr 30 Heizung AUS
temp["on"].update({"sa-so_time":6.15})			## 6 Uhr 15 Heizung EIN
temp["off"].update({"sa-so_time":7.30})			## 7 Uhr 30 Heizung AUS
temp["topic"]={"sub":"Heiz/stat/Heiz_HA0"}
temp["topic"].update({"pub":"Heiz/cmd/Heiz_HA0"})
#temp["topic"]["data_type":"int"
SENSOR_config_array.update({"Control":{"Temperierung":temp}})

temp={}
# Kühlen : in Übergangszeit Pufferspeicher kühlen
temp["Grenztemperatur"]={"unten":60}		## unter dieser Temp. Kühlung aus
temp["Grenztemperatur"].update({"oben":80})	## über dieser Temp. Kühlung ein
SENSOR_config_array["Control"]["Kuehlung"]=temp

##--------------------------------------------------------------------##
##--------------------------------------------------------------------##
##       unterhalb von hier ist normalerweise nichts zu ändern        ##
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
mqtt_client.on_message = mod_mqtt.on_mqtt_message_arrive
mqtt_client.username_pw_set(username=mqtt_client_settings["username"],password=mqtt_client_settings["password"])
# # print("Connecting...")
mqtt_client.connect(mqtt_client_settings["url"],1883)
# # print("Connecting...OK")
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
SolP_run=False
SolP_timeset=-999				## First run
# HeizP_vor_Temperierung=-999		## First run
t_WZ_t=0.0

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

			if any(debug_level_str in {"lokalSQL","remoteSQL"} for debug_level_str in builtins.debug_info_level):
				##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data
				print()
				print()
				print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+" in  MAIN while -> cloud_send_data SQL for CHART  #"+str(chart_nr))
			ret=mod_sql.make_SQLstring(chart_nr,SENSOR_config_array)
			A10_localDB.execute_sql(ret["sql_string"])
			IoTCloud.cloud_send_data(ret)
			if any(debug_level_str in {"lokalSQL","remoteSQL"} for debug_level_str in builtins.debug_info_level):
				##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data
				print ("                  SQL String="+ret["sql_string"])
				print ("###############  -> cloud_send_data SQL END   ##")
				print ()
				print ()

	######################################################

	# if any(debug_level_str in {"lokalSQL","remoteSQL"} for debug_level_str in debug_info_level):
	print('{0:>30} {1:<30} '.format(temp[0],temp[1])+temp[2])

	#############################
	####   SolarP override  #####
	#############################

	####      FROST Schutz  #####
	#############################
	Frostschutz_laufzeit=8
	Frostschutz_Grenztemp=-9.0
	t_SolP_09=mod_sensoren.get_one_sensor("uCdach/DS1820/288E0095F0013CD3",SENSOR_config_array)  # Dach Wimmerl Außentemperatur

	if (t_SolP_09 < Frostschutz_Grenztemp) and (t_SolP_09 != -100):
		if "frost" in debug_info_level :   ##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
			print("       FROSTSCHUZ!!!", \
					"     SolP_run =",SolP_run, \
					"     aktuelle Minute=", datetime.datetime.now().minute, \
					"     aktuelle Dach Temp=",t_SolP_09, \
					"     Frostschutz_Grenztemp=",Frostschutz_Grenztemp, \
					)
		if (datetime.datetime.now().minute in {11, 30}) and (SolP_run==False):
			if "frost" in debug_info_level :   ##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
				print("                          Solarpumpe EIN",datetime.datetime.now())
			SolP_timeset = datetime.datetime.now().minute
			mod_mqtt.mqtt_publish(mqtt_client,"Heiz/cmd/SolarP_override",1,"int")
			SolP_run=True
		if "frost" in debug_info_level and SolP_run:   ##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
			print ("                              ", \
				"gestartet Minute : ",SolP_timeset, \
				"läuft noch : ",SolP_timeset-datetime.datetime.now().minute+Frostschutz_laufzeit," Minuten" \
				)
		if ((datetime.datetime.now().minute - SolP_timeset) > Frostschutz_laufzeit) and (SolP_run==True):
			mod_mqtt.mqtt_publish(mqtt_client,"Heiz/cmd/SolarP_override",0,"int")
			SolP_run=False
			if "frost" in debug_info_level :   ##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
				print(" FROSTSCHUTZ Zeitende -> SolPumpe AUS")
	elif (SolP_run==True) and (t_SolP_09 != -100) :
		if "frost" in debug_info_level :   ##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
			print(" Kein FROSTSCHUTZ -> SolPumpe AUS")
		mod_mqtt.mqtt_publish(mqtt_client,"Heiz/cmd/SolarP_override",0,"int")
		SolP_run=False
	else :
		if "frost" in debug_info_level :   ##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
			print("       frostschutz called", \
					"     aktuelle Dach Temp=",t_SolP_09, \
					"     Frostschutz_Grenztemp=",Frostschutz_Grenztemp, \
					)

	###############################
	####    10Sekunden Impuls  ####
	###############################
	if time.time()- old_10seconds > 10 :

		###############################
		####    DS1820 on GPIO     ####
		debug_str="gpio"
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print()
			print()
			print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> cooling Schutz START   ##")
		t_WZ_t=mod_DS1820.get_gpio_ds1820()
		mod_mqtt.mqtt_publish(mqtt_client,"nodered/DS1820/10-000802e0ff5e",t_WZ_t,"")
		old_10seconds=time.time()
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print ("###############  -> cooling Schutz END   ##")
			print()
			print()

		###############################
		####      cooling Schutz   ####
		debug_str="cloud"
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print()
			print()
			print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> cooling Schutz START   ##")
		mqtt_message=IoTCloud.fetch_cloud_data("SolarP_override")
		if isinstance(mqtt_message, int):   ## The isinstance() function returns True if the specified object is of the specified type, otherwise False.
			mod_mqtt.mqtt_message = str(mqtt_message)
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			# print(inspect.stack()[1][1],":",inspect.stack()[1][2],":",inspect.stack()[1][3])
			print("               "+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> SolarP override fetch="+mqtt_message)
			# logging.info(__file__+' -> main got value-> SolarP override'+mqtt_message)
		if (mqtt_message!=-999):
			# topic=SENSOR_config_array["Control"]["Temperierung"]["topic"]["pub"]
			# mqtt_publish(mqtt_client,"Heiz/cmd/SolarP",mqtt_message,"int")
			mod_mqtt.mqtt_publish(mqtt_client,"Heiz/cmd/SolarP_override",mqtt_message,"int")
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			print ("############### -> cooling Schutz END    ####")
			print()
			print()


		##################################
		####   Temperierung (Bad/WZ)  ####
		debug_str="Temperierung"
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data cloud
			print()
			print()
			print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  in  MAIN while -> Temperierung START   ##")

		topic=SENSOR_config_array["Control"]["Temperierung"]["topic"]["pub"]
		HeizHA0_ist = SENSOR_config_array["Sensors"]["Heiz/stat/Heiz_HA0"]["values"]["val_aktuell"]
		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			print ('            Temperierung : (SENSOR_config_array["Control"]["Temperierung"]["HeizHA0_merk"]) =',SENSOR_config_array["Control"]["Temperierung"]["HeizHA0_merk"])
			print ('            Temperierung : (topic=',topic,' Sensor...["Heiz/stat/Heiz_HA0"]["values"][val_aktuell])  HeizHA0_ist =',HeizHA0_ist)
			print()

		if SENSOR_config_array["Control"]["Temperierung"]["HeizHA0_merk"] == -988 and SENSOR_config_array["Sensors"]["Heiz/stat/Heiz_HA0"]["values"]["val_aktuell"] != -111:
						## siehe A10_mod_sensor.prepare_sensor_array()
			##  Wenn 1. Durchlauf und ein reguläres Datum von mqtt für HeizHA0_ist vorhanden ###
			SENSOR_config_array["Control"]["Temperierung"]["HeizHA0_merk"]=HeizHA0_ist
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print ("            Temperierung: 1. Durchlauf HeizHA0_merk =  HeizHA0_ist")
		else:
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print ("            Temperierung: nicht 1. Durchlauf oder noch kein gültiges Datum vom mqtt stat/HeizP_HA0_ist")

		if SENSOR_config_array["Control"]["Temperierung"]["HeizHA0_merk"] != -988 :
			#### Wenn nicht 1. Durchlauf ####
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print ("            Temperierung: nicht 1. Durchlauf (=>und schon reguläres Datum von mqtt HeizHA0_ist vorhanden)")
			Temperierung_cmd=Control.check_Temperierung_time()
			# topic=SENSOR_config_array["Control"]["Temperierung"]["topic"]["pub"]
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print ("            "+__file__+":"+str(inspect.currentframe().f_lineno)+"->Temperierung:Temperierung_cmd=",Temperierung_cmd)
			if Temperierung_cmd == 1 :	## Temperierung Einschalten
				SENSOR_config_array["Control"]["Temperierung"]["HeizHA0_merk"]=HeizHA0_ist
				HeizHA0_cmd = "1"		## HAND
				mod_mqtt.mqtt_publish(mqtt_client,topic,HeizHA0_cmd,"")
				mod_mqtt.mqtt_publish(mqtt_client,"Heiz/cmd/info/HeizP_cmd","a"+HeizHA0_cmd,"")
				if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
					print("            Temperierung: Heizfenster -> Heizbefehl =",Temperierung_cmd, \
								" es wird via MQTT HeizHA0_cmd geschickt. ",topic," ",HeizHA0_cmd)
			if Temperierung_cmd == -1 :	## Temperierung Ausschalten
				HeizHA0_cmd = SENSOR_config_array["Control"]["Temperierung"]["HeizHA0_merk"]
				mod_mqtt.mqtt_publish(mqtt_client,topic,HeizHA0_cmd,"")
				mod_mqtt.mqtt_publish(mqtt_client,"Heiz/cmd/info/HeizP_cmd","b"+HeizHA0_cmd,"")
				if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
					print("            Temperierung: Heizfenster -> Heizbefehl =",Temperierung_cmd, \
								" es wird via MQTT HeizHA0_cmd retour gesetzt. ",topic," ",HeizHA0_cmd)
			if Temperierung_cmd == 0 :	## Temperierung nixtun
				if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
					print("            Temperierung: Heizfenster -> Heizbefehl =",Temperierung_cmd, \
								" es wird nix gemacht")
		else:
			if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
				print ("            Temperierung: Temperierung (HeizHA0_merk)=",SENSOR_config_array["Control"]["Temperierung"]["HeizHA0_merk"])
				print ("            Temperierung: 1.Durchlauf!!!")
				print()

		if any(debug_level_str in {debug_str,""} for debug_level_str in builtins.debug_info_level):
			print ("############### -> Temperierung END    ####")
			print()
			print()
		####     Temperierung END    ####
		###############################

	sleep(1) # Stop maxing out CPU
	#print ("\n------ ca 1 Sekunde\n")
exit()

