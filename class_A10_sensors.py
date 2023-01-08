#!/usr/bin/env python
# coding: utf8
import builtins
import logging
from collections import defaultdict
import time
import copy

class deal_with_sensorData:
	"""
	A class to deal with DATA comming in unregularily timeintervals
	holding the maxValue in this timeinterval to store in DB for charts.
	Data which is string and not convertible to float can be 'translated'

	...

	Attributes
	----------
	config_data : DICT
		a dictionary witch holds the data and config vars
			config_data["Sensors"]= DICT
				holds data for Sensors like TOPIC,NAME,ActualVal...

			config_data["chartDBStuff"]= DICT
				holds config data for each chart like
					timeinterval to store
					table name in DB

	Methods
	-------
	"""
	def __init__(self, config_data):
		self.SensorData=defaultdict(set)
		self.SensorData=config_data["Sensors"]
		self.chartDBStuff=defaultdict(set)
		self.chartDBStuff=config_data["chartDBStuff"]
		self.SENSOR_config_array_generic=defaultdict(set)
		self.SENSOR_config_array_generic=config_data["SENSOR_config_array_generic"]
		self.SensorMemory_prototype=defaultdict(set)
		self.SensorMemory_prototype["valData"]={"val_max":-100}

		# self.prepare_sensor_array()


	def make_DataString(self,chart_nr):
		"""
			Takes the data of all sensors defines in MAIN under ['Sensors']
			SENSOR_config_array_generic["Sensors"] part
			Returns the INSERT SQL string for all sensors.
			Table name corresponds to chart (stored in
				config_data["chartDBStuff"][chart_nr] part

			Parameters
			----------
			chart_nr : int
				Number of chart, chartdata and tablename should be taken
		"""
		sql_key=""
		sql_val=""
		cloud_string="{";
		table=self.chartDBStuff[chart_nr]["DBTable_name"]
		print("##########   make_DataString ###############")
		for Sensor_topic in self.SensorData: ## go through all def. Sensors
			if chart_nr in self.SensorData[Sensor_topic]["chart_data"]:
				if self.SensorData[Sensor_topic]['name'] in self.chartDBStuff[chart_nr]["DBTable_ColnamesNames"]:
					sql_key=sql_key+self.SensorData[Sensor_topic]['name']+","
					sql_val=sql_val+str(self.SensorData[Sensor_topic]["chart_data"][chart_nr]["val_max"])+","
					cloud_string=cloud_string+"'"+self.SensorData[Sensor_topic]['name']+"':'"
					cloud_string=cloud_string+str(self.SensorData[Sensor_topic]["chart_data"][chart_nr]["val_max"])+"',"
					## after using the sensordata of spec. chart an sensor for SQL string
					## fill the max "bucket" of this sensor and spec chart with -100.
					## Less then -100 will never be possible, so the next incomming mqttval of thissensor
					## will be bigger! That's how we get the maximum val within the timeperiod for the charts.
					## If it is a sensortype where we do not want to maximize the value over the timeperiod,
					##       SensorData["topic/path"]["val_direkt"]=1
					## we always want the last known value - do nothing
				if not "val_direkt" in self.SensorData[Sensor_topic] :
					self.SensorData[Sensor_topic]["chart_data"][chart_nr]["val_max"]=-100
			# if len(cloud_string)>0:
			cloud_string=cloud_string+"}"
			# }
		if len(sql_key)>0:
			sql_key=sql_key+'timestamp'
			sql_val=sql_val+"'"+str(int(time.time()))+"'"
			sql="INSERT INTO "+table+" ("+sql_key+") VALUES ("+sql_val+")"+";"
		else:
			sql=""
		ret=defaultdict(set)
		ret["sql_string"]=sql
		ret["cloud"]=cloud_string
		return ret


	def xxxxxget_one_sensor(self,topic):
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
		print([self.SensorData[topic]])
		try:
			if topic in self.SensorData :
				pass
			return self.SensorData[topic]["chart_data"][1]["val_max"]
			# return 555
		except:
			return -666
		########  ACHTUNG : das Topic muß in DB eingetragen sein !!!!!

	def data_insert(self,topic,val_string,Sensor_data):
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

		try:
			val=float(val_string)
		except:
			if val_string in self.SENSOR_config_array_generic["translate"]:
				val=self.SENSOR_config_array_generic["translate"][val_string]
			else:
				val=-9999
		if "datatype" in self.SensorData[topic]:
			if self.SensorData[topic]["datatype"]=="int":
				val=int(val)
		self.SensorData[topic]['val_aktuell']=val
		if "factor" in self.SensorData[topic]:
			val=val / self.SensorData[topic]["factor"]
		self.SensorData[topic]['val_aktuell']=val

		temp1="data_insert -> "+topic+" - "+self.SensorData[topic]["name"]
		temp2=bcolors.OK
		temp3="val_akt="+str(val)
		temp4=bcolors.RESET
		temp6=""
		temp7=""
		for chart_nr in self.SensorData[topic]["chart_data"]:
			temp7=" / val_max_old="+str(self.SensorData[topic]["chart_data"][chart_nr]["val_max"])
			if "val_direkt" in self.SensorData[topic]:
				self.SensorData[topic]["chart_data"][chart_nr]["val_max"] = val
			else:
				if val > self.SensorData[topic]["chart_data"][chart_nr]["val_max"]:
					self.SensorData[topic]["chart_data"][chart_nr]["val_max"] = val
					temp6="-----> Umspeichern"
				else:
					pass
			temp5=" / val_max="+str(self.SensorData[topic]["chart_data"][chart_nr]["val_max"])
			if any(debug_level_str in {"print_incomming_data",""} for debug_level_str in builtins.debug_info_level):
				##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish print_incomming_data
				print('{0:<50} {1:>6} {2:<20} {3:<6} {4:<15} {5:>20} {6:>10} '.format(temp1,temp2,temp3,temp4,temp5,temp6,temp7))



	def xxxxxxxxprepare_sensors(self):
		"""
			Builds the DICT Dictionaries used to store data for charts
			will be called just once at startup/define
			Parameters
			----------
			none
		"""
		# # print("\n\n##########  prepare_sensorMemory   #################")
		Sensor_temp={}

		## go through all defined sensors
		for Sensor_topic in self.SensorData:
			temp={}
			Sensor_temp[Sensor_topic]=copy.deepcopy(self.SensorData[Sensor_topic])

			## go through all defined charts for this sensor
			for chart_nr in self.chartDBStuff:
				## This sensor must be  defined as collumn in database table for this chart.
				if self.SensorData[Sensor_topic]["name"] in self.chartDBStuff[chart_nr]["DBTable_ColnamesNames"]:
					## Prepare the mxVall (only) for the first time with a realy low val
					## The values schould never be possible to go under this val!!!!!
					Sensor_temp[Sensor_topic]["val_aktuell"] = -111
					for key,val in self.SensorMemory_prototype["valData"].items():
						temp[chart_nr]={key:val}
					Sensor_temp[Sensor_topic]["chart_data"]=copy.deepcopy(temp)
				else:
					pass
			## If there is not at least one column for this sensor in DB - delete it
			## so we collect no data for this sensor at all
			if not "chart_data" in Sensor_temp[Sensor_topic]:
				Sensor_temp.pop(Sensor_topic)
				pass

		self.SensorData=copy.deepcopy(Sensor_temp)

	def prepare_sensor_array(self):
		"""
			Builds the DICT Dictionaries used to store data for charts
			will be called just once at startup/define
			Parameters
			----------
			none
		"""
		return
		# # print("\n\n##########  prepare_sensorMemory   #################")
		Sensor_temp={}
		print("sub->prepare_sensor_array")
		## go through all defined sensors
		for Sensor_topic in self.SensorData:
			# print ("prepare_sensor_array:Sensor_topic",Sensor_topic)
			chart_data_prototype={}
			Sensor_temp[Sensor_topic]=copy.deepcopy(self.SensorData[Sensor_topic])
			Sensor_temp[Sensor_topic]["values"]["val_aktuell"] = -111
			for chart_nr in self.chartDBStuff:
				for key,val in self.SensorMemory_prototype["valData"].items():
					chart_data_prototype[chart_nr]={key:val}
				# Sensor_temp[Sensor_topic]["chart_data"]=copy.deepcopy(temp)
				Sensor_temp[Sensor_topic]["chart_data"]=chart_data_prototype
		# self.SensorData=copy.deepcopy(Sensor_temp)
		return Sensor_temp


class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR
