import mysql.connector
import os

class Menu:
    TABLE_MAPPING = {
        "Chess": 2,
        "UNO": 1,
        "Carrom": 3
    }

    def __init__(self):
        self.mydb = None
        self.cursor = None
        self.game = None

    def connect_to_database(self):
        try:
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="kartik",
                password="Kartik84@",
                database="KARTIK",
                port=3306,
            )
            self.cursor = self.mydb.cursor()
            print("Connected to the database!")
        except mysql.connector.Error as error:
            print("Failed to connect to the database:", error)

    def close_database_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.mydb and self.mydb.is_connected():
            self.mydb.close()
            print("Disconnected from the database!")

    def get_table_name(self, game):
        table_id = self.TABLE_MAPPING.get(game)
        if table_id is None:
            return None

        self.cursor.execute("SELECT NAME FROM Inventory WHERE ID = %s", (table_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_score(self):
        tablename = self.get_table_name(self.game)
        if not tablename:
            print("Invalid game!")
            return

        name = input("Enter the Player Name: ")
        score = input("Enter the Score: ")

        try:
            query = "SELECT COUNT(*) FROM {} WHERE CODE = %s".format(tablename)
            self.cursor.execute(query, (name[0:1],))
            result = self.cursor.fetchone()
            if result[0] > 0:
                print("Record Already Exists")
            else:
                query = "INSERT INTO {} (name, score, code) VALUES (%s, %s, %s)".format(tablename)
                self.cursor.execute(query, (name, score, name[0:1]))
                self.mydb.commit()
        except mysql.connector.Error as error:
            print("Error occurred while adding score:", error)

    def show_score(self):
        tablename = self.get_table_name(self.game)
        if not tablename:
            print("Invalid game!")
            return

        try:
            query = "SELECT * FROM {}".format(tablename)
            self.cursor.execute(query)
            myresult = self.cursor.fetchall()
            for row in myresult:
                print(row)
        except mysql.connector.Error as error:
            print("Error occurred while showing score:", error)

    def update_score(self):
        tablename = self.get_table_name(self.game)
        if not tablename:
            print("Invalid game!")
            return

        name = input("Enter the Player Name: ")

        try:
            query = "UPDATE {} SET SCORE = SCORE + 1 WHERE code=%s".format(tablename)
            self.cursor.execute(query, (name[0:1],))
            self.mydb.commit()
        except mysql.connector.Error as error:
            print("Error occurred while updating score:", error)

    def revert(self):
        tablename = self.get_table_name(self.game)
        if not tablename:
            print("Invalid game!")
            return

        try:
            query = "DELETE FROM Logs WHERE LOGDATE = CURDATE()"
            self.cursor.execute(query)

            query = "INSERT INTO Logs SELECT NAME, SCORE, CURDATE() FROM UNO"
            self.cursor.execute(query)

            query = "UPDATE {} SET SCORE = 0".format(tablename)
            self.cursor.execute(query)

            self.mydb.commit()
        except mysql.connector.Error as error:
            print("Error occurred while reverting:", error)

    def reset_score(self):
        tablename = self.get_table_name(self.game)
        if not tablename:
            print("Invalid game!")
            return

        try:
            query = "UPDATE {} SET SCORE = 0".format(tablename)
            self.cursor.execute(query)
            self.mydb.commit()
        except mysql.connector.Error as error:
            print("Error occurred while resetting score:", error)

    def housekeep(self):
        tablename = self.get_table_name(self.game)
        if not tablename:
            print("Invalid game!")
            return

        try:
            query = "DELETE FROM {}".format(tablename)
            self.cursor.execute(query)
            self.mydb.commit()
        except mysql.connector.Error as error:
            print("Error occurred while performing housekeeping:", error)

    def service_status(self):
        try:
            self.cursor.execute("DELETE FROM Services")
            self.mydb.commit()

            services = {
                "SSH": "ssh",
                "Apache": "apache2",
                "MSSQL": "mysql"
            }

            for service_name, service_cmd in services.items():
                query = os.system("/etc/init.d/{} status | grep -i running 1>/dev/null 2>/dev/null".format(service_cmd))
                if query > 0:
                    self.cursor.execute("INSERT INTO Services VALUES(%s, 'Not Running', 'Y')", (service_name,))
                    print("{} Is Not Running. Please Check.".format(service_name))
                else:
                    self.cursor.execute("INSERT INTO Services VALUES(%s, 'Running', 'N')", (service_name,))
                    print("{} Is Up And Running.".format(service_name))

            self.mydb.commit()
        except mysql.connector.Error as error:
            print("Error occurred while checking service status:", error)

    def show_service_status(self):
        try:
            self.cursor.execute("SELECT Name, Status FROM Services")
            myresult = self.cursor.fetchall()
            for row in myresult:
                print(row)
        except mysql.connector.Error as error:
            print("Error occurred while showing service status:", error)

    def start_stop_restart_service(self, name, action):
        service_cmd = {
            "start": "/etc/init.d/{} start",
            "stop": "/etc/init.d/{} stop 1",
            "restart": "/etc/init.d/{} restart 1"
        }

        if name not in service_cmd:
            print("Invalid service!")
            return

        cmd = service_cmd[action].format(name)
        print(cmd)
        os.system(cmd)

    def run_menu(self):
        self.connect_to_database()
        self.game = input("Enter the Game being played: ")

        while True:
            print("1. Add Score")
            print("2. Show Score")
            print("3. Update Score")
            print("4. Reset Score")
            print("5. Housekeeping")
            print("6. Revert")
            print("7. Others")
            print("8. Exit")
            print("9. Services")
            print("10. Show Services Status")
            print("11. Start Services")
            print("12. Stop Services")
            print("13. Restart Services")

            choice = input("Enter your choice: ")

            if choice == "8":
                break
            elif choice == "1":
                self.add_score()
            elif choice == "2":
                self.show_score()
            elif choice == "3":
                self.update_score()
            elif choice == "4":
                self.reset_score()
            elif choice == "5":
                self.housekeep()
            elif choice == "6":
                self.revert()
            elif choice == "7":
                table_name = self.get_table_name(self.game)
                if table_name:
                    print(table_name)
                else:
                    print("Invalid game!")
            elif choice == "9":
                self.service_status()
            elif choice == "10":
                self.show_service_status()
            elif choice in ["11", "12", "13"]:
                name = input("Enter the service name: ")
                if choice == "11":
                    self.start_stop_restart_service(name, "start")
                elif choice == "12":
                    self.start_stop_restart_service(name, "stop")
                elif choice == "13":
                    self.start_stop_restart_service(name, "restart")
            else:
                print("Invalid choice!")

        self.close_database_connection()


m = Menu()
m.run_menu()
