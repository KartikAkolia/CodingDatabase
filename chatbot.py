#!/usr/bin/env python3
import os
import subprocess
import _mysql_connector

l=[]
source=""
dest=""

directory = os.fsencode("/dev/pts")

def bash():
    os.system("clear")
    while True:
        ch = input("bash:")
        run_command(ch)
        if ch.upper() == "EXIT":
            break

def run_command(cmd):
    os.system(cmd)

def send_msg(msg, d):
    cmd = "echo " + msg + ">" + d
    print(cmd)
    os.system(cmd)

def chat():
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        l.append(filename)
    l.sort()
    ctr = len(l) - 2
    source = "/dev/pts/" + str(l[ctr])
    dest = "/dev/pts/" + str(l[ctr - 1])
    os.system("clear")
    msg = input("$")
    # send_msg(msg, sys.argv[1])
    input("Press Key to send message")
    send_msg(msg, dest)

def init():
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        l.append(filename)
    l.sort()
    print(l)
    ctr =len(l) - 2
    source="/dev/pts/" + str(l[ctr])
    dest="/dev/pts/" + str(l[ctr-1])
    print(source,dest)

def search_string(ch, filename):
    lines = []
    flag = False
    i = 0
    result = ""
    user = ""
    y = ""
    with open(filename) as flip:
        lines = flip.readlines()
    user = ch.upper()
    for i in range(0, len(lines)):
        if user.upper() in lines[i].upper():
            flag = True
            break
    if flag:
        y = lines[i].split(":")
        i = len(y) - 1
        while i > 0:
            result = y[i] + ' ' + result
            i = i - 1
        return result
    else:
        return "0"
    flip.close()


print("Welcome To Python3_ChatBot")
#init()
while True:
    q = input("$")
    s = search_string(q, "answers.txt")
    if s == "0":
        exit()
    if "CHECK" in s.upper():
        subprocess.run(["python3", "check.py"])
    elif "MENU" in s.upper():
        subprocess.run(["python3", "New_Updated_Menu.py"])
    elif "FILE" in s.upper():
        subprocess.run(["python3", "file.py", "data.txt"])
    elif "MATH" in s.upper():
        subprocess.run(["python3", "math.py"])
    elif "BASH" in s.upper():
        bash()
    elif "CHAT" in s.upper():
        chat()
    else:
        print(s)


# def check_process():
#    mydb = mysql.connector.connect(
#                host="192.168.0.102",
#                user="kartik",
#                password="Kartik84@",
#                database="KARTIK",
#                port=3306
#            )
#    cursor = mydb.cursor()
#    #machine_id = sp.getoutput("ps auxwww | grep -i 'python3 messaging_service.py' | awk '{print $7}' | head -1")
#    machine_id = sp.getoutput("tty")
#    get_ip=sp.getoutput("ifconfig -a | grep -i inet | head -1 | awk '{print $2}'")
#    system = sp.getoutput("ps auxwww | grep -i 'python3 messaging_service.py' | awk '{print $12}' | head -1")
#    cursor.execute("INSERT INTO system_id VALUES('" + machine_id + "','" + system + "','" + get_ip + "', 'Y')")
#    mydb.commit()
#    cursor.close()