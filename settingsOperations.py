import json
import os





## zapisuje ustawienia w pliku JSON
def saveSettings_JSON(settings): 
    if os.path.exists("outputs") == False: os.mkdir("outputs") 
    with open("outputs\\settings.json", "w") as outfile:
        data = { "currency": settings.currency, "fixing": settings.fixing, "data_source": settings.data_source }
        json_object = json.dumps(data, indent=3)
        outfile.write(json_object)
        




## zapisuje ustawienia domyślne w pliku JSON 
def createDefaultSettings(settings):
    settings.currency = 'PLN'
    settings.fixing = 1
    settings.data_source = 1

    if os.path.exists("outputs") == False: os.mkdir("outputs") 
    with open("outputs\\settings.json", "w") as outfile:
        data = { "currency": settings.currency, "fixing": settings.fixing, "data_source": settings.data_source }
        json_object = json.dumps(data, indent=3)
        outfile.write(json_object)





## ładuje ustawienia z pliku JSON
def loadSettings(settings):
    filePath = "outputs\\settings.json"
    
    if os.path.exists(filePath):  ## jeśli plik istnieje 
        fileSize = os.path.getsize(filePath)
        if fileSize >= 55  and  fileSize <= 75:  ## jeśli plik ma w sobie jakieś dane
            with open(filePath) as outfile:
                data = json.load(outfile)

                settings.currency = data["currency"]
                settings.fixing = data["fixing"]
                settings.data_source = data["data_source"]
        else: 
            createDefaultSettings(settings)
    else:
        createDefaultSettings(settings)
    