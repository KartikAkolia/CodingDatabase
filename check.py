import os

def print_menu():
    print("1 /etc/init.d/ssh status")
    print("2 /etc/init.d/ssh start")
    print("3 /etc/init.d/ssh stop")
    print("4 /etc/init.d/ssh restart")
    print("5 /etc/init.d/apache2 status")
    print("6 /etc/init.d/apache2 start")
    print("7 /etc/init.d/apache2 stop")
    print("8 /etc/init.d/apache2 restart")
    print("9 /etc/init.d/mysql status")
    print("10 /etc/init.d/mysql start")
    print("11 /etc/init.d/mysql stop")
    print("12 /etc/init.d/mysql restart")
    print("13 Update and Upgrade")
    print("14 Exit")


def execute_command(command):
    os.system(command)

def main():
    while True:
        print_menu()
        choice = input("Enter Your Choice: ")

        if choice == "1":
            execute_command("/etc/init.d/ssh status")
        elif choice == "2":
            execute_command("/etc/init.d/apache2 status")
        elif choice == "3":
            execute_command("/etc/init.d/mysql status")
        elif choice == "4":
            execute_command("/etc/init.d/ssh start")
        elif choice == "5":
            execute_command("/etc/init.d/apache2 start")
        elif choice == "6":
            execute_command("/etc/init.d/mysql start")
        elif choice == "7":
            execute_command("/etc/init.d/ssh stop")
        elif choice == "8":
            execute_command("/etc/init.d/apache2 stop")
        elif choice == "9":
            execute_command("/etc/init.d/mysql stop")
        elif choice == "10":
            execute_command("/etc/init.d/ssh restart")
        elif choice == "11":
            execute_command("/etc/init.d/apache2 restart")
        elif choice == "12":
            execute_command("/etc/init.d/mysql restart")
        elif choice == "13":
            execute_command("/etc/init.d/ssh reload")
        elif choice == "14":
            execute_command("/etc/init.d/apache2 reload")
        elif choice == "15":
            execute_command("/etc/init.d/mysql reload")
        elif choice == "16":
            execute_command("sudo apt update -y && sudo apt full-upgrade -y && sudo apt autoremove -y && sudo apt clean -y && sudo apt autoclean -y")
        elif choice == "17":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
