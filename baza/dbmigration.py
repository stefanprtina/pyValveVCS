import sqlite3

try:
    conn = sqlite3.connect('baza/baza.db')

    conn.execute('''CREATE TABLE IF NOT EXISTS firme
             (ID INT PRIMARY KEY     NOT NULL,
             naziv          TEXT    NOT NULL,
             podaci            TEXT     NOT NULL
             )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS ventili
             (id INT PRIMARY KEY     NOT NULL,
             firma         INT    NOT NULL,
             serbroj            TEXT     NOT NULL,
             lokacija            TEXT     NOT NULL,
             precnik            TEXT    NOT NULL,
             medij              TEXT    NOT NULL,
             pritisak           TEXT    NOT NULL
             )''')
    print("Migracija uspjesna.")
except:
    print("Migracija neuspjesna")




conn.close()