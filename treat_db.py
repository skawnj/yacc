import sqlite3

with sqlite3.connect('db.sqlite3') as conn:
    cur = conn.cursor()

