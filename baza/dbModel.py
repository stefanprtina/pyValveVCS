import sqlite3

class dbModel():
    def __init__(self, parent):
        self.parent = parent

    def connect(self):
        try:
            dbConn = sqlite3.connect('baza/baza.db')
            print("Konekcija uspjesna!")
            return dbConn
        except Exception as err:
            print("Konekcija neuspjesna")
            print(str(err))


