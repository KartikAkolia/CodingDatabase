class menu:
    import mysql.connector 
    import os

    def __init__(self,ch):
        self.ch=3
        self.mydb = self.mysql.connector.connect(
        host="localhost",
        user="kartik",
        password='Kartik84@',
        database='KARTIK',
        port=3306
        )
    def get_tablename(self):
        cursor = self.mydb.cursor()
        cursor.execute("SELECT NAME FROM Inventory WHERE ID=1")
        result=cursor.fetchone()
        cursor.close()
        return result [0]
    def add_score(self):
        tablename=self.get_tablename()
        n=input("Enter The Player Name")
        s=input("Enter The Score")
        cursor = self.mydb.cursor()
        cursor.execute("SELECT COUNT(*) FROM " + tablename + " WHERE CODE='" + n[0:1] + "'")
        result=cursor.fetchone()
        if result[0]>0:
            print("Record Already Exists")
            print(cursor.rowcount)
        else:
            query=("insert into " + tablename + " (name,score,code) VALUES (%s,%s,'" + n[0:1] + "')")
            print(query)
            cursor.execute(query,(n,s))
            self.mydb.commit()
            cursor.close()

    def show_score(self):
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT * FROM UNO")
        myresult = mycursor.fetchall()
        for x in myresult:
            print(x)
            print(type(myresult))
            mycursor.close()

    def update_score(self):
        n=input("Enter The Player Name")
        if self.mydb.is_connected:
            print('Connection successfully established!')
            query=("UPDATE UNO SET SCORE= score + 1" + " where code='" + n[0:1] + "'")
            print(query)
            cursor = self.mydb.cursor()
            cursor.execute(query)
            self.mydb.commit()

    def revert(self):
        query=("DELETE FROM Logs WHERE LOGDATE=CURDATE()")
        cursor = self.mydb.cursor()
        cursor.execute(query)
        query=("INSERT INTO Logs SELECT NAME,SCORE,CURDATE() FROM UNO")
        cursor = self.mydb.cursor()
        cursor.execute(query)
        query=("UPDATE UNO SET SCORE=0")
        print(query)
        cursor = self.mydb.cursor()
        cursor.execute(query)
        self.mydb.commit()
        cursor.close()

    def reset_score(self):
        query=("UPDATE UNO SET SCORE=0")
        print(query)
        cursor = self.mydb.cursor()
        cursor.execute(query)
        self.mydb.commit()
        cursor.close()


    def housekeep(self):
        query=("DELETE FROM UNO")
        cursor = self.mydb.cursor()
        cursor.execute(query)
        self.mydb.commit()
        cursor.close()

    def Service_Status(self):
        cursor = self.mydb.cursor()
        cursor.execute("DELETE FROM  Services")
        self.mydb.commit()
        cursor.close()
        query=self.os.system("/etc/init.d/ssh status | grep -i running 1>/dev/null 2>/dev/null")
        if query>0:
            cursor = self.mydb.cursor()
            cursor.execute("INSERT INTO Services VALUES('SSH','Not Running', 'Y')")
            print("SSH Is Not Running Please Check")
            input("Press Any Key")
        else:
            cursor = self.mydb.cursor()
            cursor.execute("INSERT INTO Services VALUES('SSH','Running', 'N')")
            print("SSH Is Up And Running")
            input("Press Any Key")
        self.mydb.commit()
        cursor.close()
	
        query=self.os.system("/etc/init.d/apache2 status | grep -i running 1>/dev/null 2>/dev/null")
        if query>0:
            cursor = self.mydb.cursor()
            cursor.execute("INSERT INTO Services VALUES('Apache','Not Running', 'Y')")
            print("Apache Is Not Running Please Check")
            input("Press Any Key")
        else:
            cursor = self.mydb.cursor()
            cursor.execute("INSERT INTO Services VALUES('Apache','Running', 'N')")
            print("Apache Is Up And Running")
            input("Press Any Key")
        self.mydb.commit()
        cursor.close()
	
        query=self.os.system("/etc/init.d/mysql status | grep -i running 1>/dev/null 2>/dev/null")
        if query>0:
            cursor = self.mydb.cursor()
            cursor.execute("INSERT INTO Services VALUES('MSSQL','Not Running', 'Y')")
            print("MSSQL Is Not Running Please Check")
            input("Press Any Key")
        else:
            cursor = self.mydb.cursor()
            cursor.execute("INSERT INTO Services VALUES('MSSQL','Running', 'N')")
            print("MSSQL Is Up And Running")
            input("Press Any Key")
        self.mydb.commit()
        cursor.close()

    def Show_Service_Status(self):
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT Name, Status FROM Services")
        myresult = mycursor.fetchall()
        for x in myresult:
            print(x)
            mycursor.close()
    
    def Start_Service(self,name):
        start_s="/etc/init.d/"+ name + " start"
        print(start_s)
        self.os.system(start_s)

    def Stop_Service(self,name):
        stop_s="/etc/init.d/"+ name + " stop 1"
        print(stop_s)
        self.os.system(stop_s)
    
    def Show_Service(self,name):
        show_s="/etc/init.d/"+ name + " status"
        print(show_s)
        self.os.system(show_s)
    
    def Restart_Services(self,name):
        restart_s="/etc/init.d/"+ name + " restart 1"
        print(restart_s)
        self.os.system(restart_s)

m=menu(3)
while m.ch != '3':
  print("1 add_score")
  print("2 show_score")
  print("3 update_score")
  print("4. Reset Score")
  print("5. Housekeeping")
  print("6. Revert")
  print("7. Others")
  print("8. Exit")
  print("9 Services")
  print("10 Show_Services_Status")
  print("11 Start_Services")
  print("12 Stop_Services")
  print("13 Restart_Services")
  
  m.ch=input("Enter Your Choice")
  if m.ch=='8':
    exit()
  if m.ch=='1':
    m.add_score()
  if m.ch=='2':
    m.show_score()
  if m.ch=='3':
    m.update_score()
  if m.ch=='4':
    m.reset_score()
  if m.ch=='5':
    m.housekeep()
  if m.ch=='6':
    m.revert()
  if m.ch=='7':
    i=m.get_tablename()
    print(i)
  if m.ch=='9':
    m.Services_Status()
  if m.ch=='10':
    name=input("Which Services see the status?")
    m.Show_Service(name)
  if m.ch=='11':
    name=input("Which Services to start?")
    m.Start_Service(name)
  if m.ch=='12':
       name=input("Which Services to stop?")
       m.Stop_Service(name)
  if m.ch=='13':
      name=input("Which Services to restart?")
      m.Restart_Service(name)
