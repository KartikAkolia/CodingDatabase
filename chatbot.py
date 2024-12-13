#!/usr/bin/env python3
import os
import subprocess

# Constants for the PTS directory
directory = "/dev/pts"

# Welcome message
print("Welcome To Python3_ChatBot")

def bash():
    """Simulates a bash terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        ch = input("bash:")
        if ch.strip().upper() == "EXIT":
            break
        run_command(ch)

def run_command(cmd):
    """Runs a system command."""
    try:
        if isinstance(cmd, str):
            subprocess.run(cmd.split(), check=True)
        else:
            print("Invalid command format.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def send_msg(msg, dest):
    """Sends a message to a specific PTS destination."""
    try:
        with open(dest, "w") as dest_file:
            dest_file.write(msg + "\n")
    except Exception as e:
        print(f"Failed to send message: {e}")

def chat():
    """Facilitates chat between two PTS sessions."""
    try:
        pts_files = sorted(
            [file for file in os.listdir(directory) if file.isdigit()],
            key=lambda x: int(x)
        )
        if len(pts_files) < 2:
            print("Not enough PTS terminals for chat.")
            return

        source = os.path.join(directory, pts_files[-1])
        dest = os.path.join(directory, pts_files[-2])

        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Chat source: {source}, destination: {dest}")
        while True:
            msg = input("$")
            if msg.strip().upper() == "EXIT":
                print("Exiting chat...")
                break
            send_msg(msg, dest)
    except Exception as e:
        print(f"Chat error: {e}")

def search_string(keyword, filename):
    """Searches for a string in a file and returns the result."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()

        for line in lines:
            if keyword.upper() in line.upper():
                return line.split(":", 1)[-1].strip()
        return "0"
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return "0"
    except Exception as e:
        print(f"Error searching file: {e}")
        return "0"

running = True
while running:
    try:
        q = input("$").strip()
        if not q:
            continue

        response = search_string(q, "answers.txt")
        if response == "0":
            print("No match found. Exiting.")
            running = False
            break

        if "CHECK" in response.upper():
            subprocess.run(["python3", "check.py"])
        elif "MENU" in response.upper():
            subprocess.run(["python3", "New_Updated_Menu.py"])
        elif "FILE" in response.upper():
            subprocess.run(["python3", "file.py", "data.txt"])
        elif "BASH" in response.upper():
            bash()
        elif "CHAT" in response.upper():
            chat()
        else:
            print(response)
    except KeyboardInterrupt:
        print("\nExiting chatbot. Goodbye!")
        running = False
        break
    except Exception as e:
        print(f"Unexpected error: {e}")
