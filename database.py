import MySQLdb as mdb

class dbConnection():
    try:
        mydb = mdb.connect(
            host="localhost",
            user="root",
            password="",
            database="ams_database"
        )
        print("Connection Successful to the Database")
        mycursor = mydb.cursor()
    except mdb.Error as e:
        print("Connection Failed to the Database")
