ctr=0
username=["Kartik", "Jake", "Jacob"]
password=["KAR","JAK", "JAC"]

while True:
    u=input("Enter Your Username")
    p=input("Enter Your Password")

    if u==username[0] and password[0]:
        print("Hello There " + u)
    if u==username[1] and password[1]:
        print("Hello There " + u)
    if u==username[2] and password[2]:
        print("Hello There " + u)
    if u!=username[0] + username[1] + username[2] and password[0] + password[1] + password[2]:
        print("Please Enter either username or password again, First Entry Used, the Maximum Attempts is three")
        ctr=ctr+1
    if ctr>3:
        print("Maximum Entries Entered Please try again later")
        exit()
