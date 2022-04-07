#!/usr/bin/env python3
import os
ch = '0'
while True:
    print("1 /etc/init.d/ssh status")
    print("2 /etc/init.d/apache2 status")
    print("3 /etc/init.d/mysql status")
    print("4 /etc/init.d/ssh start")
    print("5 /etc/init.d/apache2 start")
    print("6 /etc/init.d/mysql start")
    print("7 /etc/init.d/ssh stop")
    print("8 /etc/init.d/apache2 stop")
    print("9 /etc/init.d/mysql stop")
    print("10 /etc/init.d/ssh restart")
    print("11 /etc/init.d/apache2 restart")
    print("12 /etc/init.d/mysql restart")
    print("13 /etc/init.d/ssh reload")
    print("14 /etc/init.d/apache2 reload")
    print("15 /etc/init.d/mysql reload")
    print("16 sudo apt update -y && sudo apt full-upgrade -y && sudo apt autoremove -y && sudo apt clean -y && sudo apt autoclean -y")
    print("17 exit")
    ch = input("Enter Your Choice")
    if ch == '1':
        os.system("/etc/init.d/ssh status | grep -i running")
    if ch == '2':
        os.system("/etc/init.d/apache2 status | grep -i running")
    if ch == '3':
        os.system("/etc/init.d/mysql status | grep -i running")
    if ch == '4':
        os.system("/etc/init.d/ssh start")
    if ch == '5':
        os.system("/etc/init.d/apache2 start")
    if ch == '6':
        os.system("/etc/init.d/mysql start")
    if ch == '7':
        os.system("/etc/init.d/ssh stop")
    if ch == '8':
        os.system("/etc/init.d/apache2 stop")
    if ch == '9':
        os.system("/etc/init.d/mysql stop")
    if ch == '10':
        os.system("/etc/init.d/ssh restart")
    if ch == '11':
        os.system("/etc/init.d/apache2 restart")
    if ch == '12':
        os.system("/etc/init.d/mysql restart")
    if ch == '13':
        os.system("/etc/init.d/ssh reload")
    if ch == '14':
        os.system("/etc/init.d/apache2 reload")
    if ch == '15':
        os.system("/etc/init.d/mysql reload")
    if ch == '16':
        os.system("sudo apt update -y && sudo apt full-upgrade -y && sudo apt autoremove -y && sudo apt clean -y && sudo apt autoclean -y")
    if ch == '17':
        exit()
