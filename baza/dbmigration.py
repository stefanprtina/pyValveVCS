import sqlite3

try:
    conn = sqlite3.connect('baza/baza.db')

    conn.execute('''CREATE TABLE IF NOT EXISTS firme
             (
             naziv          TEXT    NOT NULL,
             podaci            TEXT     NOT NULL
             )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS ventili
             (
             firma         INT    NOT NULL,
             serbroj            TEXT     NOT NULL,
             lokacija            TEXT     NOT NULL,
             precnik            TEXT    NOT NULL,
             medij              TEXT    NOT NULL,
             pritisak           TEXT    NOT NULL
             )''')
    conn.commit()
    print("Migracija uspjesna.")

except:
    print("Migracija neuspjesna")

conn.close()