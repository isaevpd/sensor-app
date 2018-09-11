"""Create and populate iot_db.sqlite database"""

import sqlite3
import time
import random

SENSORS = ['abba', 'acdc', 'iddqd', 'idkfa']
DB_NAME = 'iot_db.sqlite'
ITEM_COUNT = 12500000
# Time is stored to databse in unix epoch
# To convert it in sql queries you might need to use
# e.g. datetime(time, 'unixepoch')
INITIAL_TIME = int(time.time())


def init_db():
    """Re-create database tables and indexes"""

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS datas')
    cursor.execute('CREATE TABLE datas (id TEXT, time TIMESTAMP, value REAL)')
    cursor.execute('CREATE INDEX main_idx on datas (id, time)')
    conn.commit()
    conn.close()


def insert_data(sensor_id):
    """Insert ITEM_COUNT rows of data for sensor_id"""

    def calculate_value(initial):
        """Add or reduce value with 0.005, but keep between 16 and 29"""
        mod = random.uniform(-0.005, 0.005)
        # Keep value between 16 and 29
        if 16 < initial + mod > 29:
            return initial - mod
        else:
            return initial + mod

    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()

    temperature = 22
    items = []
    current_time = INITIAL_TIME

    for _ in range(0, ITEM_COUNT):
        # Reduce time with x seconds for each data point
        current_time = current_time - 5
        temperature = calculate_value(temperature)
        items.append((sensor_id, current_time, temperature))

    cursor.executemany('INSERT INTO datas VALUES (?,?,?)', items)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()

    start_time = time.time()

    [insert_data(x) for x in SENSORS]

    print("--- %s seconds ---" % (time.time() - start_time))
