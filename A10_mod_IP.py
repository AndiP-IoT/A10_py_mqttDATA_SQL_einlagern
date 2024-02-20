#!/usr/bin/env python
# coding: utf8
# import paho.mqtt.client as paho
import A10_mod_mqtt as mod_mqtt
import os
import builtins
# import logging
import inspect
# import time
# import subprocess
# import platform

def get_IP(mqtt_client):
	debug_str="ip"
	if any(debug_level_str in {debug_str,"modulecall",""} for debug_level_str in builtins.debug_info_level):
		print()
		print ("###############"+__file__+":"+str(inspect.currentframe().f_lineno)+"  -> get_IP   ##")
		print()
	ipv4 = os.popen('ip addr show eth0 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip()
	# print(ipv4)
	mod_mqtt.mqtt_publish(mqtt_client,"info/ipv4/NRpython",ipv4,"")






def ping(host):
	"""
	Returns True if host (str) responds to a ping request.
	Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
	"""

	# Option for the number of packets as a function of
	param = '-n' if platform.system().lower()=='windows' else '-c'
	# Building the command. Ex: "ping -c 1 google.com"
	command = ['ping', param, '1', "-w", "1",  host]
	# command = os.popen(f"ping -c 1 {IP_to_ping} ").read()
	# Pinging each IP address 4 times
	# IP_connected=mod_IP.ping(IP_to_ping)
	# IP_connected = subprocess.Popen(["/bin/ping", "-c1", "-w1", IP_to_ping], stdout=subprocess.PIPE).stdout.read()

	result = subprocess.run(command, stdout=subprocess.PIPE)
	print("  ---> response ",result, end = ' ')



	output = result.stdout.decode('utf8')
	if "Request timed out." in output or "100% packet loss" in output or "Host Unreachable" in output:
		return "NOT CONNECTED"
	return "CONNECTED"


