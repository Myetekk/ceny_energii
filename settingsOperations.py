import json
import os
import datetime

# from utils import saveError





## zapisuje ustawienia w pliku JSON
def saveSettings_JSON(settings, errors): 
    try:
        if os.path.exists("outputs") == False: os.mkdir("outputs") 
        with open("outputs\\settings.json", "w") as outfile:
            data = { "currency": str(settings.currency), "fixing": int(settings.fixing), "data_source": int(settings.data_source) }
            json_object = json.dumps(data, indent=3)
            outfile.write(json_object)
                
    except Exception as e:
        print(f"An error occurred in saveSettings_JSON: {e}. Trying again")
        saveError(str(e) + "  in saveSettings_JSON")
        errors.errorNumber += 1
        createDefaultSettings(settings, errors)
        




## zapisuje ustawienia domyślne w pliku JSON 
def createDefaultSettings(settings, errors):
    settings.currency = 'PLN'
    settings.fixing = 1
    settings.data_source = 1

    try:
        if os.path.exists("outputs") == False: os.mkdir("outputs") 
        with open("outputs\\settings.json", "w") as outfile:
            data = { "currency": str(settings.currency), "fixing": int(settings.fixing), "data_source": int(settings.data_source) }
            json_object = json.dumps(data, indent=3)
            outfile.write(json_object)

    except Exception as e:
        print(f"An error occurred in createDefaultSettings: {e}. Trying again")
        saveError(str(e) + "  in createDefaultSettings")
        errors.errorNumber += 1





## ładuje ustawienia z pliku JSON
def loadSettings(settings, errors):
    filePath = "outputs\\settings.json"
    
    try:
        if os.path.exists(filePath):  ## jeśli plik istnieje 
            fileSize = os.path.getsize(filePath)
            if fileSize >= 55  and  fileSize <= 75:  ## jeśli plik ma w sobie jakieś dane
                with open(filePath) as outfile:
                    data = json.load(outfile)

                    settings.currency = str(data["currency"])
                    settings.fixing = int(data["fixing"])
                    settings.data_source = int(data["data_source"])
            else: 
                createDefaultSettings(settings, errors)
        else:
            createDefaultSettings(settings, errors)
        
    except Exception as e:
        print(f"An error occurred in loadSettings: {e}. Trying again")
        saveError(str(e) + "  in loadSettings")
        errors.errorNumber += 1
        createDefaultSettings(settings, errors)










def saveError(message):
    try:
        if os.path.exists("outputs") == False: os.mkdir("outputs") 
        fileName = "outputs\\errors.txt"

        file = open(fileName, "a")
        errorText = str(datetime.datetime.now()) + "  " + str(message) + "\n"
        file.write(errorText)
        file.close()

    except Exception as e:
        print(f"An error occurred in saveError: {e}.")