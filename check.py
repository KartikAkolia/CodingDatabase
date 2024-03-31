import os
import subprocess

# Define the services and their corresponding commands
SERVICES = {
    "1": {"name": "ssh", "command": "/etc/init.d/ssh"},
    "2": {"name": "apache2", "command": "/etc/init.d/apache2"},
    "3": {"name": "mysql", "command": "/etc/init.d/mysql"}
}

# Define the actions that can be performed on the services
ACTIONS = {
    "1": "status",
    "2": "start",
    "3": "stop",
    "4": "restart"
}

def print_menu():
    # Print the available services
    print("Select a service:")
    for key, service in SERVICES.items():
        print(f"{key} {service['name']}")
    print("4 Update and Upgrade")
    print("5 Exit")

def print_actions():
    # Print the available actions
    print("Select an action:")
    for key, action in ACTIONS.items():
        print(f"{key} {action}")

def execute_command(command):
    # Execute the command and handle any errors
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command `{command}` failed with exit status {e.returncode}")

def main():
    while True:
        print_menu()
        service_choice = input("Enter Your Choice: ")

        if service_choice == "4":
            # Perform system update and upgrade
            execute_command("sudo apt update -y && sudo apt full-upgrade -y && sudo apt autoremove -y && sudo apt clean -y && sudo apt autoclean -y")
        elif service_choice == "5":
            # Exit the program
            break
        elif service_choice in SERVICES:
            print_actions()
            action_choice = input("Enter Your Choice: ")
            if action_choice in ACTIONS:
                # Construct the command and execute it
                command = f"{SERVICES[service_choice]['command']} {ACTIONS[action_choice]}"
                execute_command(command)
            else:
                print("Invalid action choice. Please try again.")
        else:
            print("Invalid service choice. Please try again.")

if __name__ == "__main__":
    main()
