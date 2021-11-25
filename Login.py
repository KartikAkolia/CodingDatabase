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
    #if (u!=username[0] or u!=username[1] or u!=username[2]) and (p!=password[0] or p!=password[1] or p!=password[2]):
    #    print("Please Enter either username or password again, First Entry Used, the Maximum Attempts is three")
    #    ctr=ctr+1
    if ctr>3:
        print("Maximum Entries Entered Please try again later")
        exit()
