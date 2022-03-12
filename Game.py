import random
score=0
username=["Admin","Kartik","Person","Guest"]
password=["admin","KAR14","person","guest"]
u=input("Enter Your Username")
p=input("Enter Your Password")
def checking():
    if u!=username[0]:
        if u!=username[1]:
            if u!=username[2]:
                if u!=username[3]:
                    print("Wrong Username Entered")
    if p!=password[0]:
        if p!=password[1]:
            if p!=password[2]:
                if p!=password[3]:
                    print("Wrong Password Entered")
checking()
x=random.randint(0,6)
value=int(input("Enter A Number"))
if value > x:
    score=score+1
    print( u + " entered value is " + str(value) + " The random value was " + str(x) + " The score is " + str(score))
if value < x:
    score=score-1
    print( u + " entered value is " + str(value) + " The random value was " + str(x) + " The score is " + str(score))