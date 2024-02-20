#!/usr/bin/env python
# coding: utf8
import builtins
import logging
import inspect
import sqlite3
#import mysql
# import mariadb
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
		# try: self.mariadb_connection = mariadb.connect(
		try: self.db_connection = sqlite3.connect(
							# user=config_data["user"],
							# password=config_data["password"],
							# host=config_data["host"],
							# port=config_data["port"],
							database=config_data["database"]
						)
		except self.sqlite3.Error as err:
			print("Something went wrong: {}".format(err))
			sys.exit(1)
		self.db_sql = self.db_connection.cursor()
		# self.db_connection.autocommit = True

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
		# self.db_sql.execute("SELECT name FROM sqlite_master WHERE type='table';")
		self.db_sql.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = '"+DBtable_name+"';")
		# print(self.db_sql.fetchall())
		table_exist=0
		for name in self.db_sql.fetchall():
			print("fields in #",DBtable_name,"# -> ")
			print("#",name[0],"#")
			# print ("ja")
			table_exist=1
			self.db_sql.execute("Select * FROM "+DBtable_name+" LIMIT 0 ")
			self.colnames = [desc[0] for desc in self.db_sql.description]
			print (self.colnames)
			return self.colnames
		# print ("no")
		return 0

	def execute_sql(self,sql_string):
		"""
			Executes the given sql_string directly in DB

			Parameters
			----------
			sql_string : str
				The SQL string itselfs
		"""
		print ("                     "+__file__+":"+str(inspect.currentframe().f_lineno)+	" -> execute_sql --> SQL -> DB\n")
		print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+	" --> "+sql_string)
		print ("wertzuiopoiuztrewertzuiuztre",sql_string)
		self.db_sql.execute(
			sql_string
		)
		self.db_connection.commit()

