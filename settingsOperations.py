import json
import os
import sqlite3
import datetime





## zapisuje ustawienia w pliku JSON
def saveSettings_JSON(settings, errors): 
    try:
        if os.path.exists("outputs") == False: os.mkdir("outputs") 
        with open("outputs\\settings.json", "w") as outfile:
            data = { "currency": str(settings.currency), "fixing": int(settings.fixing), "data_source": int(settings.data_source), "updateTime": int(settings.updateTime), "entsoeKey": str(settings.entsoeKey) }
            json_object = json.dumps(data, indent=3)
            outfile.write(json_object)


    except Exception as e:
        print(f"An error occurred in saveSettings_JSON: {e}. Trying again")
        saveError(str(e) + "  in saveSettings_JSON")
        errors.errorNumber += 1
        createDefaultSettings(settings, errors)
        




## ustawia ustawienia domyślne i zapisuje w pliku JSON 
def createDefaultSettings(settings, errors):
    settings.currency = 'PLN'
    settings.fixing = 2
    settings.data_source = 2
    settings.updateTime = 3600
    settings.entsoeKey = 'd2f433b7-ab33-4210-8328-15b9462f7316'

    try:
        if os.path.exists("outputs") == False: os.mkdir("outputs") 
        with open("outputs\\settings.json", "w") as outfile:
            data = { "currency": str(settings.currency), "fixing": int(settings.fixing), "data_source": int(settings.data_source), "updateTime": int(settings.updateTime), "entsoeKey": str(settings.entsoeKey) }
            json_object = json.dumps(data, indent=3)
            outfile.write(json_object)


    except Exception as e:
        print(f"An error occurred in createDefaultSettings: {e}. Trying again")
        saveError(str(e) + "  in createDefaultSettings")
        errors.errorNumber += 1





## ładuje ustawienia z pliku JSON, jeśli napotka jakieś problemy  -->  ustawia ustawienia domyślne
def loadSettings(settings, errors):
    filePath = "outputs\\settings.json"
    
    try:
        if os.path.exists(filePath):  ## jeśli plik istnieje 
            fileSize = os.path.getsize(filePath)
            if fileSize >= 135  and  fileSize <= 155:  ## jeśli plik ma w sobie jakieś dane i są odpowiednio długie
                with open(filePath) as outfile:
                    data = json.load(outfile)

                    settings.currency = str(data["currency"])
                    settings.fixing = int(data["fixing"])
                    settings.data_source = int(data["data_source"])
                    settings.updateTime = int(data["updateTime"])
                    settings.entsoeKey = str(data["entsoeKey"])
            else: 
                createDefaultSettings(settings, errors)
        else:
            createDefaultSettings(settings, errors)
        
        
    except Exception as e:
        print(f"An error occurred in loadSettings: {e}. Using default settings")
        saveError(str(e) + "  in loadSettings")
        errors.errorNumber += 1
        createDefaultSettings(settings, errors)










## loguje błędy do bazy danych;   ta sama funkcja co w 'utils.py', poniewać circular import
def saveError(message):
    try:
        path = "outputs\\dataBase.db"
        conn = sqlite3.connect(path)
        cur = conn.cursor()

        sql1 ='''CREATE TABLE IF NOT EXISTS errors (
            date	TEXT NOT NULL,
            message	TEXT NOT NULL
        );'''
        cur.execute(sql1)

        sql2 ='''INSERT INTO errors (date, message) VALUES (?, ?);'''
        cur.execute(sql2, [str(datetime.datetime.now()), str(message)])

        conn.commit()
        conn.close()


    except Exception as e:
        print(f"An error occurred in saveError: {e}.")
