#!/usr/bin/env python
# coding: utf8
import copy


def prepare_sensor_array(SENSOR_config_array):
	"""
		Builds the DICT Dictionaries used to store data for charts
		will be called just once at startup/define
		Parameters
		----------
		none
	"""
	# # print("\n\n##########  prepare_sensorMemory   #################")
	Sensor_temp={}
	print("#################    sub->prepare_sensor_array")
	## go through all defined sensors
	for Sensor_topic in SENSOR_config_array["Sensors"]:
		####  allen Sensoren ein Feld für letzten (über Bus,mqtt...) bekommenen Wert
		SENSOR_config_array["Sensors"][Sensor_topic]["values"]={"val_aktuell":-111}

		####  allen Sensoren für alle Charts, die definiert sind, ein Feld definieren,
		####			dessen Inhalt dann in die DB eingetragen wird
		####			max_val oder direkt_val oder Mittelwert oder .....
		for chart_nr in SENSOR_config_array["chartDBStuff"]:
			Sensor_temp[chart_nr]={"val_for_chart":-100}
		SENSOR_config_array["Sensors"][Sensor_topic]["chart_data"]=copy.deepcopy(Sensor_temp)

def get_one_sensor(topic,SENSOR_config_array):
	"""
		Returns the data of a sensors (topic).

		Parameters
		----------
		topic : string
			Sensor topic to determine specific sensor

		Returns
		----------
		val : string
			Actual value of this sensor
	"""
	# print([SENSOR_config_array["Sensors"][topic]])
	try:
		if topic in SENSOR_config_array["Sensors"] :
			pass
		return SENSOR_config_array["Sensors"][topic]["chart_data"][1]["val_for_chart"]
		# return 555
	except:
		return -100
	########  ACHTUNG : das Topic muß in DB eingetragen sein !!!!!
