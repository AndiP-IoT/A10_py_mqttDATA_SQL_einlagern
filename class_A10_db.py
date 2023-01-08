#!/usr/bin/env python
# coding: utf8
import builtins
import logging
import mariadb
import sys
from collections import defaultdict
import time



class ChartData_DBTables:
	"""
	A class used to deal with MariaDB database
		storing Data for CHARTS

	...

	Attributes
	----------
	config_data : DICT
		a dictionary witch holds the DB credentials
			config_data["user"]="DBuser"
			config_data["password"]="DBuser-pwd"
			config_data["host"]="127.0.0.1"
			config_data["port"]=3306
			config_data["database"]="DBname"

	Methods
	-------
	get_col_headers(DBtable_name)
		Returns the ColNames from Table given.
	execute_sql(sql_string)
		Executes the given SQLstring in DB
	"""
	# https://realpython.com/documenting-python-code/
	def __init__(self,config_data):
		"""
			Takes the DB credentials
			Connects to DB

			Parameters
			----------
			config_data : DICT
				The Credentials
		"""
 		# Connect to MariaDB Platform
		# self.config_data=dict(config_data)
		try: self.mariadb_connection = mariadb.connect(
							user=config_data["user"],
							password=config_data["password"],
							host=config_data["host"],
							port=config_data["port"],
							database=config_data["database"]
						)
		except mariadb.Error as err:
			print("Something went wrong: {}".format(err))
			sys.exit(1)
		self.mariadb_sql = self.mariadb_connection.cursor()
		self.mariadb_connection.autocommit = True

	def get_col_headers(self,DBtable_name):
		"""
			Takes the ColNames from the given Table in configured DB
			Returns them as an ARRAY

			Parameters
			----------
			DBtable_name : str
				The Name of Table in DB
		"""
        # ###### Funktioniert, aber aufwendige Umwandlung ?
		# sql="""SHOW TABLES"""
		# self.mariadb_sql.execute(sql)
		# results = self.mariadb_sql.fetchall()
		# print (results)

		# ###### NICHT geeignet bei MariaDB
		# sql="SELECT * FROM information_schema.tables WHERE table_name = 'chartData_5'"
		# self.mariadb_sql.execute(sql)
		# self.colnames = [desc[0] for desc in self.mariadb_sql.description]
		# print (self.colnames)
		# print (DBtable)
		sql = "SHOW TABLES LIKE '"+DBtable_name+"'"
		self.mariadb_sql.execute(sql)
		result = self.mariadb_sql.fetchone()
		# print ("Wertzuioiuztrertzuztr")
		if result:
			# print ("OK")
			self.mariadb_sql.execute("Select * FROM "+DBtable_name+" LIMIT 0")
			self.colnames = [desc[0] for desc in self.mariadb_sql.description]
			# for Sensor_topic in self.colnames:
				# print ("wwww",Sensor_topic)
			# for Sensor_topic in self.SensorData:
				# if self.SensorData[Sensor_topic]["name"] in self.colnames:
					# print ("gefunden")
				# print (Sensor_topic)
			return self.colnames
			# there is a table named .....
		else:
			# print ("NoNoNo")
			return 0
			# there are no tables named .....

	def execute_sql(self,sql_string):
		"""
			Executes the given sql_string directly in DB

			Parameters
			----------
			sql_string : str
				The SQL string itselfs
		"""
		self.mariadb_sql.execute(
			sql_string
		)
		self.mariadb_connection.commit()

