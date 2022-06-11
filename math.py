#!/usr/bin/env python3 
import math
def add(x,y):
    return(x+y)
def subtract(x,y):
    return(x-y)
def multiply(x,y):
    return(x*y)
def divide(x,y):
    return(x/y)
def sqrt():
    print(math.sqrt())
print("1.Add")
print("2.Subtract")
print("3.Multiply")
print("4.Divide")
print("5.Sqaure_Root")
while True:
    choice=input("Enter Choice '1','2','3','4','5'")
    if choice in('1','2','3','4','5'):
        if choice=='5':
            square_root=int(float(input("Enter Value")))
            print(math.sqrt(square_root))   
    if choice !='5':    
        num1=int(float(input("Enter First Number")))
        num2=int(float(input("Enter Second Number")))
    if choice=='1':
        print(num1, "+", num2, "=", add(num1, num2))
    if choice=='2':
        print(num1, "-", num2, "=", subtract(num1, num2))
    if choice=='3':
        print(num1, "*", num2, "=", multiply(num1, num2))
    if choice=='4':
        print(num1, "/", num2, "=", divide(num1, num2))
    next_calculation = input("Let's do next calculation? (yes/no): ")
    if next_calculation == "no":
        break
