import subprocess

while True:
    print("1 check.py")
    print("1A check.py_Vim")
    print("2 file.py")
    print("2A file.py_Vim")
    print("3 Updated_Menu.py")
    print("3A Updated_Menu.py_Vim")
    user = input("Enter Number From Menu")
    if user == "1":
        subprocess.run(
            ["python3", "/home/kartikakolia/Linux_Python3_Projects/check.py"]
        )
    if user == "1A":
        subprocess.run(["vim", "/home/kartikakolia/Linux_Python3_Projects/check.py"])
    if user == "2":
        subprocess.run(
            [
                "python3",
                "/home/kartikakolia/Linux_Python3_Projects/file.py",
                "hello.txt",
            ]
        )
    if user == "2A":
        subprocess.run(["vim", "/home/kartikakolia/Linux_Python3_Projects/file.py"])
    if user == "3":
        subprocess.run(
            ["python3", "/home/kartikakolia/Linux_Python3_Projects/Updated_Menu.py"]
        )
    if user == "3A":
        subprocess.run(
            ["vim", "/home/kartikakolia/Linux_Python3_Projects/Updated_Menu.py"]
        )
