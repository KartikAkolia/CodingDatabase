import subprocess, os

ch = "0"


def checkpy():
    while True:
        print("1 /etc/init.d/ssh status")
        print("2 /etc/init.d/apache2 status")
        print("3 /etc/init.d/mysql status")
        print("4 /etc/init.d/ssh start")
        print("5 /etc/init.d/apache2 start")
        print("6 /etc/init.d/mysql start")
        print("7 /etc/init.d/ssh stop")
        print("8 /etc/init.d/apache2 stop")
        print("9 /etc/init.d/mysql stop")
        print("10 /etc/init.d/ssh restart")
        print("11 /etc/init.d/apache2 restart")
        print("12 /etc/init.d/mysql restart")
        print("13 /etc/init.d/ssh reload")
        print("14 /etc/init.d/apache2 reload")
        print("15 /etc/init.d/mysql reload")
        print(
            "16 sudo apt update -y && sudo apt full-upgrade -y && sudo apt autoremove -y && sudo apt clean -y && sudo apt autoclean -y"
        )
        print("17 exit")
        ch = input("Enter Your Choice")

    if ch == "1":
        subprocess.run(["os.system", "/etc/init.d/ssh status"])
        input("Press Any Key To Continue")
    if ch == "2":
        subprocess.run(["os.system", "/etc/init.d/apache2 status"])
        input("Press Any Key To Continue")
    if ch == "3":
        subprocess.run(["os.system", "/etc/init.d/mysql status"])
        input("Press Any Key To Continue")
    if ch == "4":
        subprocess.run(["os.system", "/etc/init.d/ssh start"])
        input("Press Any Key To Continue")
    if ch == "5":
        subprocess.run(["os.system", "/etc/init.d/apache2 start"])
        input("Press Any Key To Continue")
    if ch == "6":
        subprocess.run(["os.system", "/etc/init.d/mysql start"])
        input("Press Any Key To Continue")
    if ch == "7":
        subprocess.run(["os.system", "/etc/init.d/ssh stop"])
        input("Press Any Key To Continue")
    if ch == "8":
        subprocess.run(["os.system", "/etc/init.d/apache2 stop"])
        input("Press Any Key To Continue")
    if ch == "9":
        subprocess.run(["os.system", "/etc/init.d/mysql stop"])
        input("Press Any Key To Continue")
    if ch == "10":
        subprocess.run(["os.system", "/etc/init.d/ssh restart"])
        input("Press Any Key To Continue")
    if ch == "11":
        subprocess.run(["os.system", "/etc/init.d/apache2 restart"])
        input("Press Any Key To Continue")
    if ch == "12":
        subprocess.run(["os.system", "/etc/init.d/mysql restart"])
        input("Press Any Key To Continue")
    if ch == "13":
        subprocess.run(["os.system", "/etc/init.d/ssh reload"])
        input("Press Any Key To Continue")
    if ch == "14":
        subprocess.run(["os.system", "/etc/init.d/apache2 reload"])
        input("Press Any Key To Continue")
    if ch == "15":
        subprocess.run(["os.system", "/etc/init.d/mysql reload"])
        input("Press Any Key To Continue")
    if ch == "16":
        subprocess.run(
            [
                "os.system",
                "sudo apt update -y && sudo apt full-upgrade -y && sudo apt autoremove -y && sudo apt clean -y && sudo apt autoclean -y",
            ]
        )
        input("Press Any Key To Continue")


checkpy()
