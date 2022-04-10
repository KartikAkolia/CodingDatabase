#!/usr/bin/env python3
import sys
import time

#Searching A Word in a text file
def search_string():
    lines=[]
    flag=False
    i=0
    with open("hello.txt") as flip:
        lines=flip.readlines()
    user=input("Enter word for searching? ")
    for i in range(0,len(lines)-1):
        if user in lines[i]:
            flag=True
            break
    if flag==True:
        print(lines[i])
    else:
        print("String doesn't exist")

def tail_file():
    lines=[]
    tail_lines=[]
    with open("hello.txt") as flip:
        lines=flip.readlines()
    i=len(lines)-1
    while i >= len(lines)-2:
        tail_lines.insert(i,lines[i]) 
        i=i-1
    j=len(tail_lines)-1
    while j >=0:
        print (tail_lines[j], end = '')
        j=j-1

def head_file():
    lines=[]
    with open("hello.txt") as flip:
        lines=flip.readlines()
    i=len(lines)-3
    while int(i) <= int(len(lines)-1):
        print(lines[i])
        i=i+1
ch=0
while ch!=5:
    print("1 Search for single word")
    print("2 Tail The File")
    print("3 Exit")
    ch=input("Enter Your Choice")
    if int(ch) ==1:
        search_string()
    if int(ch) ==2:
        tail_file() 
    if int(ch) ==3:
        exit()