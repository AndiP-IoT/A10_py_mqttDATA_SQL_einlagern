#!/usr/bin/env python
# coding: utf8
import builtins
import logging
import inspect
from collections import defaultdict
import time
import copy
import socket
import requests
import http.client
import json
from urllib.parse import urlparse
# import os
# import sys
thisFile = __file__

class iot_cloud:
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
	def __init__(self):
		# print (thisFile)
		pass
		url = "http://mqtt.scienceontheweb.net/test.php"
		ploads=""
		self.headers = requests.utils.default_headers()
		self.headers.update({
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
		})
		# if (self.check_site_exist(url)):
			# pass
		# self.SensorData=defaultdict(set)
		# self.SensorData=config_data["Sensors"]
		# self.chartDBStuff=defaultdict(set)
		# self.chartDBStuff=config_data["chartDBStuff"]
		# self.config_sonstiges=defaultdict(set)
		# self.config_sonstiges=config_data["config_sonstiges"]
		# self.SensorMemory_prototype=defaultdict(set)
		# self.SensorMemory_prototype["valData"]={"val_for_chart":-100}

		# self.prepare_sensors()

	def cloud_send_data(self,myobj):
		url = "http://mqtt.scienceontheweb.net/test.php"
		if any(debug_level_str in {"remoteSQL",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
			print ("               ##############   "+__file__+":"+str(inspect.currentframe().f_lineno)+" -> cloud_send_data START -->url",url)
		if (self.check_site_exist(url)):
			try:
				r = requests.post(url,data=myobj)
				if any(debug_level_str in {"remoteSQL",""} for debug_level_str in builtins.debug_info_level):
					##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
					print ("                               -> cloud_send_data-->requests.post",r)
				pass
			except requests.exceptions.RequestException as e:  # This is the correct syntax
				if any(debug_level_str in {"remoteSQL",""} for debug_level_str in builtins.debug_info_level):
					##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
					print ("                                   -> cloud_send_data-->xxxxxxxxxxxxxrequest error")
				###logging.debug(("sub:cloud_send_data->",e)
		if any(debug_level_str in {"remoteSQL",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
			print ("               ##############    "+__file__+":"+str(inspect.currentframe().f_lineno)+" ->cloud_data sent END")


	def check_site_exist(self, url):
		if any(debug_level_str in {"remoteSQL",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
			print ("               ##############    "+__file__+":"+str(inspect.currentframe().f_lineno)+" -> check_site_exist START-->url",url)
		# url = url.replace("http://","")
		url_parts = urlparse(url)
		#print ("check_site_exist-->url_parts",url_parts)

		try:
			#url_parts = urlparse(url)
			# print ("check_site_exist-->url_parts",url_parts)
			# print ("check_site_exist-->url_parts",url_parts,url_parts.scheme,url_parts.netloc)
			request = requests.head("://".join([url_parts.scheme, url_parts.netloc]))
			if any(debug_level_str in {"remoteSQL",""} for debug_level_str in builtins.debug_info_level):
				##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
				print ("               ##############    "+__file__+":"+str(inspect.currentframe().f_lineno)+" -> check_site_exist END --> OK")
			return True
		except:
			if any(debug_level_str in {"remoteSQL",""} for debug_level_str in builtins.debug_info_level):
				##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
				print ("                ##############    "+__file__+":"+str(inspect.currentframe().f_lineno)+" -> check_site_exist END -->Oh no, conection error")
			###logging.debug(("sub:check_site_exist->Oh no, conection error")
			return False


	def fetch_cloud_data(self,topic):
		if any(debug_level_str in {"remoteSQL",""} for debug_level_str in builtins.debug_info_level):
			print ("               ##############    "+__file__+":"+str(inspect.currentframe().f_lineno)+" -> fetch_cloud_data START")
		ploads="show_sensor="+topic
		url = "http://mqtt.scienceontheweb.net/test.php"
		url_exist=self.check_site_exist(url)
		# print ("WERTZ",url_exist)
		if (url_exist==False):
			# print('fetch_cloud_data--->URL NOT NOT NOT OK',url_exist)
			return -999
		else:
			# print('fetch_cloud_data--->URL OK')
			try:
				retour = requests.get(url, headers=self.headers,params=ploads,timeout=10)
				if any(debug_level_str in {"remoteSQL",""} for debug_level_str in builtins.debug_info_level):
					##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
					print ("                                -> fetch_cloud_data--->conection OK")
			except ConnectionResetError as exc:
				if any(debug_level_str in {"remoteSQL",""} for debug_level_str in builtins.debug_info_level):
					##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
					print ("                                -> fetch_cloud_data--->Oh no, conection error", str(exc))
					###logging.debug(("sub:fetch_cloud_data->Oh no, conection error")
				raise
			if any(debug_level_str in {"remoteSQL",""} for debug_level_str in builtins.debug_info_level):
				print ("                                -> fetch_cloud_data--->HTTPStatus OK")
		if any(debug_level_str in {"remoteSQL",""} for debug_level_str in builtins.debug_info_level):
			print ("                                -> fetch_cloud_data->requests.get() Wert=",retour)
		MyPythonList = eval(retour.text)
		# print("MyPythonList ",MyPythonList, " type: ",type(MyPythonList))

		y = json.loads(retour.text)
		values_view = y.values()
		value_iterator = iter(values_view)
		first_value = next(value_iterator)
		# print("first_value ",first_value, " type: ",type(first_value))

		if (first_value == "ON"):
			mqtt_massage="1"
		else :
			mqtt_massage="0"
		if (first_value == "1"):
			mqtt_massage="1"
		else :
			mqtt_massage="0"
		if any(debug_level_str in {"remoteSQL",""} for debug_level_str in builtins.debug_info_level):
			##  lokalSQL remoteSQL Temperierung cooling frost mega2560 doorbell mqtt_publish
			print ("               ##############    "+__file__+":"+str(inspect.currentframe().f_lineno)+" ->fetch_cloud_data END")
		return mqtt_massage


class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR
