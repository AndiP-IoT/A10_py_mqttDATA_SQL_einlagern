#!/usr/bin/env python
# coding: utf8
import builtins
import logging
import inspect
import time


def make_SQLstring(chart_nr,SENSOR_config_array):
	global SENSOR_NaN
	val_temp=""
	"""
		Takes the data of all sensors defines in MAIN under ['Sensors']
		config_sonstiges["Sensors"] part
		Returns the INSERT SQL string for all sensors.
		Table name corresponds to chart (stored in
			config_data["chartDBStuff"][chart_nr] part

		Parameters
		----------
		chart_nr : int
			Number of chart, chartdata and tablename should be taken
	"""
	if any(debug_level_str in {"lokalSQL","remoteSQL"} for debug_level_str in builtins.debug_info_level):
		##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish mqtt print_incomming_data
		print("               ###############"+__file__+":"+str(inspect.currentframe().f_lineno)+" -> make_SQLstring")
	table=SENSOR_config_array["chartDBStuff"][chart_nr]["DBTable_name"]
	sql_key=""
	sql_val=""
	cloud_string="{";
	for Sensor_topic in SENSOR_config_array["Sensors"]: ## go through all def. Sensors
		if chart_nr in SENSOR_config_array["Sensors"][Sensor_topic]["chart_data"]:
			if SENSOR_config_array["Sensors"][Sensor_topic]['name'] in SENSOR_config_array["chartDBStuff"][chart_nr]["DBTable_ColnamesNames"]:
				sql_key=sql_key+SENSOR_config_array["Sensors"][Sensor_topic]['name']+","
				val_temp=str(SENSOR_config_array["Sensors"][Sensor_topic]["chart_data"][chart_nr]["val_for_chart"])
				if (val_temp=="NaN"):
					val_temp="-99"
				# sql_val=sql_val+str(SENSOR_config_array["Sensors"][Sensor_topic]["chart_data"][chart_nr]["val_for_chart"])+","
				sql_val=sql_val+val_temp+","
				cloud_string=cloud_string+"'"+SENSOR_config_array["Sensors"][Sensor_topic]['name']+"':'"
				cloud_string=cloud_string+str(SENSOR_config_array["Sensors"][Sensor_topic]["chart_data"][chart_nr]["val_for_chart"])+"',"
				## after using the sensordata of spec. chart an sensor for SQL string
				## fill the max "bucket" of this sensor and spec chart with -100.
				## Less then -100 will never be possible, so the next incomming mqttval of thissensor
				## will be bigger! That's how we get the maximum val within the timeperiod for the charts.
				## If it is a sensortype where we do not want to maximize the value over the timeperiod,
				##       SensorData["topic/path"]["val_direkt"]=1
				## we always want the last known value - do nothing
			if not "val_direkt" in SENSOR_config_array["Sensors"][Sensor_topic] :
				SENSOR_config_array["Sensors"][Sensor_topic]["chart_data"][chart_nr]["val_for_chart"]=SENSOR_NaN
	cloud_string=cloud_string+"}"
	if len(sql_key)>0:
		sql_key=sql_key+'timestamp'
		sql_val=sql_val+"'"+str(int(time.time()))+"'"
		sql="INSERT INTO "+table+" ("+sql_key+") VALUES ("+sql_val+")"+";"
	else:
		sql=""
	ret={}
	ret["sql_string"]=sql
	ret["cloud"]=cloud_string
	return ret


