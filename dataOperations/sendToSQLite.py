import sqlite3
import datetime

from utils import checkNumberOfErrors, saveError





path = "outputs\\dataBase.db"

def sendToSQLite(objectList_entsoe, objectList_tge, objectList_entsoe_next, objectList_tge_next, errors, settings, window):
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

        send(objectList_entsoe, objectList_tge, objectList_entsoe_next, objectList_tge_next, date, errors)


    except Exception as e:
        print(f"An error occurred in sendToSQLite: {e}.")
        saveError(str(e) + "  in sendToSQLite")
        errors.errorNumber += 1
        if errors.errorNumber <= 20:   sendToSQLite(objectList_entsoe, objectList_tge, objectList_entsoe_next, objectList_tge_next, errors, settings, window)
        else:   checkNumberOfErrors(errors, settings, window)





def send(objectList_entsoe, objectList_tge, objectList_entsoe_next, objectList_tge_next, date, errors):
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()

        for i in range(24):
            sql ='''INSERT INTO odczyt_''' + str(date)[:10] + ''' 
                    (hours, price_entsoe, price_entsoe_next, price_tge, price_tge_next, date, upload_time) 
                    VALUES (?, ?, ?, ?, ?, ?, ?);'''
            table = [str(objectList_entsoe[i].hour), str(objectList_entsoe[i].price), str(objectList_entsoe_next[i].price), str(objectList_tge[i].price), str(objectList_tge_next[i].price), str(objectList_entsoe[i].date), str(datetime.datetime.now())[:19]]

            cur.execute(sql, table)

        
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"An error occurred in sendToSQLite: {e}.")
        saveError(str(e) + "  in sendToSQLite")
        errors.errorNumber += 1
