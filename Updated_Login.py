import numpy
names=numpy.array(["Kartik","Ashley","Oliver"])
names1=numpy.array([""])
password=numpy.array(["KAR","ASH","OLI"])
password1=numpy.array([""])


username=input("Enter your Username")
for n in names:
    if n!=username:
        names1=numpy.append(names,username)
        print("You have been added to the list")
        break
    else:
        break

passw=input("Enter your Password")
for p in password:
    if p!=passw:
        password1=numpy.append(password,passw)
        print("New Password Added")
        break
    else:
        break
