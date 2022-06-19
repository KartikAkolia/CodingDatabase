#!/usr/bin/env python3
import os


# Searching A Word in a text file
def search_string():
    result = ""
    if not os.path.exists("/home/pi/Python3_New_Development/hello.txt"):
        print("Please check if you are in the correct directory")
        return 1
    with open("hello.txt") as flip:
        lines = flip.readlines()
    user = input("Enter word for searching? ")
    for i in range(0, len(lines) - 1):
        if user.upper() in lines[i].upper():
            y = lines[i].split()
            i = len(y) - 1
            while i > 0:
                result = y[i] + ' ' + result
                i = i - 1
            print(result)
            result + "\n"
            result = ""
    flip.close()


# Tailing A File
def tail_file():
    tail_lines = []
    with open("hello.txt") as flip:
        lines = flip.readlines()
    i = len(lines) - 1
    while i >= len(lines) - 2:
        tail_lines.insert(i, lines[i])
        i = i - 1
    j = len(tail_lines) - 1
    while j >= 0:
        print(tail_lines[j], end='')
        j = j - 1


# Heading A File
def head_file():
    with open("/home/pi/Python3_New_Development/hello.txt") as flip:
        lines = flip.readlines()
    i = len(lines) - 3
    while int(i) <= int(len(lines) - 1):
        print(lines[i])
        i = i + 1


# This goes to specific line
def go_line(num):
    flip = open("/home/pi/Python3_New_Development/hello.txt")
    lines = flip.readlines()[num - 1]
    return lines


def print_line(l):
    print(go_line(l))


def writing_file():
    f = open("x.txt", "w")
    user = input("Enter String To Write")
    f.write(user)
    f.close()


ch = 0
while ch != 5:
    print("1 Search for single word")
    print("2 Tail The File")
    print("3 Display Line")
    print("4 Write To File ")
    print("5 Exit")

    ch = input("Enter Your Choice")
    if int(ch) == 1:
        search_string()
    if int(ch) == 2:
        tail_file()
    if int(ch) == 3:
        x = input("Enter Line Number")
        print_line(int(x))
    if int(ch) == 4:
        writing_file()
    if int(ch) == 5:
        exit()
