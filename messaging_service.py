#!/usr/bin/env python3
import os,sys,subprocess as sp
import mysql.connector

sender=[]
mydb=""

def check_process():
	mydb = mysql.connector.connect(
	            host="192.168.0.102",
	            user="kartik",
	            password="Kartik84@",
	            database="KARTIK",
	            port=3306
	        )
	cursor = mydb.cursor()
	#machine_id = sp.getoutput("ps auxwww | grep -i 'python3 messaging_service.py' | awk '{print $7}' | head -1")
	machine_id = sp.getoutput("tty")
	get_ip=sp.getoutput("ifconfig -a | grep -i inet | head -1 | awk '{print $2}'")
	system = sp.getoutput("ps auxwww | grep -i 'python3 messaging_service.py' | awk '{print $12}' | head -1")
	cursor.execute("INSERT INTO system_id VALUES('" + machine_id + "','" + system + "','" + get_ip + "', 'Y')")
	mydb.commit()
	cursor.close()


check_process()
input("ch")
