#!/usr/bin/env python3
import os,sys,subprocess

def bash():
    os.system("clear")
    while True:
        ch=input("bash:")
        run_command(ch)
        if ch.upper()=="EXIT":
            break

def run_command(cmd):
    os.system(cmd)

def search_string(ch,filename):
    lines=[]
    flag=False
    i=0
    result=""
    user=""
    y=""
    with open(filename) as flip:
        lines=flip.readlines()
    user=ch.upper()
    for i in range(0,len(lines)):
        if user.upper() in lines[i].upper():
            flag=True 
            break
    if flag==True:
        y=lines[i].split(":")
        i=len(y)-1
        while i > 0:
            result=y[i] + ' ' +  result
            i=i-1
        return result
    else:
        return "0"
    flip.close()

print("Welcome To Python3_ChatBot")
while True:
    q=input("$")
    s=search_string(q,"answers.txt")
    if s=="0":
        exit()
    if "CHECK" in s.upper():
       subprocess.run(["python3", "check.py"])
    elif "MENU" in s.upper():
        subprocess.run(["python3", "New_Updated_Menu.py"]) 
    elif "FILE" in s.upper():
        subprocess.run(["python3", "file.py","data.txt"])
    elif "MATH" in s.upper():
        subprocess.run(["python3", "math.py"])
    elif "BASH" in s.upper():
        bash()
    else:
        print(s)