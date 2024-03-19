import sqlite3
import time

def acquire_lock(conn):
    while True:
        try:
            conn.execute("BEGIN IMMEDIATE")
            return True
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                time.sleep(0.1)
            else:
                raise