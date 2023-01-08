#!/usr/bin/env python
# coding: utf8
import builtins
import sys
import subprocess


############ MQTT Sub procedures definieren
def on_mqtt_connect(mqtt_client, userdata, flags, rc):
	# # print("A10_mod_mqtt->sub:on_mqtt_connect->Connected with result code "+str(rc))
	mqtt_client.subscribe("#")

def on_mqtt_disconnect(mqtt_client, userdata,rc=0):
    ###logging.debug(("A10_mod_mqtt->sub:on_mqtt_disconnect->DisConnected result code "+str(rc))
    mqtt_client.loop_stop()

def on_mqtt_message_arrive(mqtt_client, userdata, msg):
	########global data_of_this_topic_memory
	### Wenn das Topic in Sensor-Topic-Def definiert ist,
	### Speichere den angekommenen Wert mit Sensor_class
	### in SensorData[topic]['val_aktuell']
	# print (["mqtt_message received",msg.topic,msg.topic == "WF/cmd/Bell" and msg.payload.decode() == "ON",msg.payload])
	if any(debug_level_str in {"mqtt",""} for debug_level_str in builtins.debug_info_level):
		##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt
		print ("A10_mod_mqtt->sub:on_mqtt_message_arrive",["mqtt_message received",msg.topic,msg.payload])
	if msg.topic == "Heiz/stat/Heiz_HA0":
		# msg.payload
		pass
	if msg.topic == "only/for/debug/self":
		pass
	if msg.topic == "only/for/debug/mega":
		# ret=defaultdict(set)
		# ret["sql_string"]="INSERT INTO `debug` (`timestamp`, `topic`, `message`) VALUES ("
		# ret["sql_string"]=ret["sql_string"]+"'"+str(int(time.time()))+"'"
		# ret["sql_string"]=ret["sql_string"]+",'"+msg.topic+"'"
		# ret["sql_string"]=ret["sql_string"]+",'"+str(msg.payload.decode())+"')"
		# IoTCloud.cloud_send_data(ret)
		if "mega2560" in debug_info_level :   ##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell
			print ("A10_mod_mqtt->sub:debug msg got from mega")
		pass
	if msg.topic == "Info":
		###logging.debug(('on message topic=%s  payl=%s', msg.topic,msg.payload)
		pass
	if msg.topic == "WF/cmd/Bell" and msg.payload.decode() == "ON":
		if "doorbell" in debug_info_level :   ##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell
			print ("A10_mod_mqtt->sub:Doorbell",msg.topic,msg.payload)
		mqtt_publish(mqtt_client,"WF/stat/Bell","ON","")
		subprocess.run("/usr/bin/python2.7 /home/pi/Scripts/python/Doorbell_RPi/doorbell.py &", shell=True, check=True)
		if "doorbell" in debug_info_level :   ##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell
			print ("A10_mod_mqtt->sub:nach doorbell play")
		pass
	if msg.topic in userdata["Sensors"]:
		# A10_sensors_class.data_insert(msg.topic,msg.payload,SENSOR_config_array["Sensors"])
		mqtt_data_insert(msg.topic,msg.payload,userdata)
		if any(debug_level_str in {"mqtt",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt
			print("A10_mod_mqtt->sub:Value eingetragen: Topic=",msg.topic," Data=",userdata["Sensors"][msg.topic])
		# print([userdata])
	pass

def mqtt_publish(mqtt_client, topic, data, datatype):
	if "mqtt_publish" in debug_info_level :   ##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
		###logging.debug(("sub:send->mptt send data / topic ")
		if any(debug_level_str in {"mqtt",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt
			print("A10_mod_mqtt->sub:send->mptt send data / topic ")
		# print(SENSOR_config_array["Sensors"])
	# try:
		# temp=SENSOR_config_array["Sensors"][topic]["datatype"]
	# except:
	if datatype == "int" :
		data=int(data)
	# if topic in SENSOR_config_array["Sensors"] :
		# if "datatype" in SENSOR_config_array["Sensors"][topic] :
			# if SENSOR_config_array["Sensors"][topic]["datatype"]=="int":
				# data=int(data)
		if any(debug_level_str in {"mqtt","mqtt_publish"} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt
			print ("A10_mod_mqtt->sub:mqtt_publish -> topic,data",topic," ",data)
	mqtt_client.publish(topic,data)


def mqtt_data_insert(Sensor_topic,val_string,Sensor_data):
	"""
		Takes the data of a sensors (topic). The value will be
		stored in in config_data["Sensors"][topic]["val_aktuell"]
		part.
		And stores the value in maxvalue if bigger than the stored
		maxvalue for each chart.
		(the maxvalue will be resetted when the SQLstring is built
			for a specific chart)
		First the value as string (val_string) will be converted to float.
		If the value string can't be converted, we have a
			translation table


		Parameters
		----------
		topic : string
			Sensor topic to determine specific sensor
		val : string
			Actual value of this sensor
	"""

	val_string=str(val_string.decode("utf-8"))
	# for Sensor_topic in Sensor_data[topic]:
		# print("sub->data_insert->topic=",Sensor_topic)

	# return
	if any(debug_level_str in {"mqtt","print_incomming_data"} for debug_level_str in builtins.debug_info_level):
		##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data
		print("##########   A10_mod_mqtt->mqtt_data_insert ###############")
	try:
		val=float(val_string)
	except:
		if val_string in Sensor_data["config_sonstiges"]["translate"]:
			val=Sensor_data["config_sonstiges"]["translate"][val_string]
		else:
			val=-9999
	if "datatype" in Sensor_data["Sensors"][Sensor_topic]:
		if Sensor_data["Sensors"][Sensor_topic]["datatype"]=="int":
			val=int(val)
		Sensor_data["Sensors"][Sensor_topic]["values"]['val_aktuell']=val
	if "factor" in Sensor_data["Sensors"][Sensor_topic]:
		val=val / Sensor_data["Sensors"][Sensor_topic]["factor"]
		Sensor_data["Sensors"][Sensor_topic]["values"]['val_aktuell']=val

	temp1="data_insert -> "+Sensor_topic+" - "+Sensor_data["Sensors"][Sensor_topic]["name"]
	temp2="" #textcolors.bcolors.OK
	temp3="val_akt="+str(val)
	temp4="" #textcolors.bcolors.RESET
	temp6=""
	temp7=""
	for chart_nr in Sensor_data["Sensors"][Sensor_topic]["chart_data"]:
		temp7=" / val_for_chart_old="+str(Sensor_data["Sensors"][Sensor_topic]["chart_data"][chart_nr]["val_for_chart"])
		if "val_direkt" in Sensor_data["Sensors"][Sensor_topic]:
			Sensor_data["Sensors"][Sensor_topic]["chart_data"][chart_nr]["val_for_chart"]=val
		else:
			if val > Sensor_data["Sensors"][Sensor_topic]["chart_data"][chart_nr]["val_for_chart"]:
				Sensor_data["Sensors"][Sensor_topic]["chart_data"][chart_nr]["val_for_chart"]=val
				temp6="-----> Umspeichern"
			else:
				pass
		temp5=" / val_for_chart="+str(Sensor_data["Sensors"][Sensor_topic]["chart_data"][chart_nr]["val_for_chart"])
		if any(debug_level_str in {"print_incomming_data","mqtt"} for debug_level_str in builtins.debug_info_level):
			pass
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish print_incomming_data
			print('{0:<50} {1:>6} {2:<20} {3:<6} {4:<15} {5:>20} {6:>10} '.format(temp1,temp2,temp3,temp4,temp5,temp6,temp7))


