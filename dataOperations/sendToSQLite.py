import sqlite3
import datetime



path = "dataBase.db"

def sendToSQLite(objectList_entsoe, objectList_tge, objectList_entsoe_next, objectList_tge_next):
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        date = objectList_entsoe[0].date.replace("-", "_")

        sql ='''CREATE TABLE IF NOT EXISTS odczyt_''' + str(date)[:10] + ''' (
                    hours	TEXT NOT NULL,
                    price_entsoe	REAL NOT NULL,
                    price_entsoe_next	REAL NOT NULL,
                    price_tge	REAL NOT NULL,
                    price_tge_next	REAL NOT NULL,
                    date	TEXT NOT NULL,
                    upload_time	TEXT NOT NULL
                );'''
        cur.execute(sql)
        conn.close()

        for i in range(24):
            send(objectList_entsoe[i], objectList_entsoe_next[i], objectList_tge[i], objectList_tge_next[i], date)
    except sqlite3.Error as e:
        print(e)





def send(object_entsoe, object_entsoe_next, object_tge, object_tge_next, date):
    conn = sqlite3.connect(path)
    cur = conn.cursor()

    sql ='''INSERT INTO odczyt_''' + str(date)[:10] + ''' 
            (hours, price_entsoe, price_entsoe_next, price_tge, price_tge_next, date, upload_time) 
            VALUES (?, ?, ?, ?, ?, ?, ?);'''

    table = [str(object_entsoe.hour), str(object_entsoe.price), str(object_entsoe_next.price), str(object_tge.price), str(object_tge_next.price), str(object_entsoe.date), str(datetime.datetime.now())[:19]]
    cur.execute(sql, table)
    conn.commit()
    conn.close()
