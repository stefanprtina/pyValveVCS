import sqlite3

class dbModel():
    def __init__(self, parent):
        self.parent = parent
        try:
            self.dbConn = sqlite3.connect('baza/baza.db')
            print("Konekcija uspjesna!")
        except Exception as err:
            print("Konekcija neuspjesna")
            print(str(err))



