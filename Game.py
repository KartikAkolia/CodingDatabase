#!/usr/bin/env python3
import random
value=[]
score=""
username=["Kartik","Neeraj"]
password=["KARIK","NERAJ".upper]
x=input("Enter Your Username")
y=input("Enter Your Password")
if x!=username[0]:
    print("Wrong Username Entered")
if x==username[1]:
    print("Correct Username Entered")
if y!=password[0]:
    print("Wrong Password Entered")
if y==password[1]:
    print("Correct Password Entered")
first_x=random.randint(0,6)
second_y=random.randint(0,6)
first_input_x=input("Enter A Digit between 0-6?")
if first_input_x < first_x:
    score=score+1
    print("Well Done " + str(username) + str(score))
