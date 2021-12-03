ctr=0
username=["Kartik", "Jake", "Jacob"]
password=["KAR","JAK", "JAC"]

while True:
    u=input("Enter Your Username")
    p=input("Enter Your Password")

    if u==username[0] and password[0]:
        print("Hello There " + u)
    else:
        ctr=ctr+1
    if u==username[1] and password[1]:
        print("Hello There " + u)        
    else:
        ctr=ctr+1
    if u==username[2] and password[2]:
        print("Hello There " + u)
    else:
        ctr=ctr+1
    if ctr>3:
        print("Maximum Entries Entered Please try again later")
        exit()
