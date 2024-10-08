import pandas as pd
import time
from entsoe import EntsoeRawClient
import datetime
from xml.dom.minidom import parseString

from utils import getEUR, increaseOneDay, saveError, tryInternetConnection





## klasa przechowująca dane zparsowane z entsoe
class Entsoe:
    date = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
    hour = 0
    price = 0.0
    euro = 1.0
    currency = 'PLN'
    fixing = 1  ## dla entsoe tylko fixing pierwszy
    data_source = 1
    status = False  ## False- bad, True- good





def resetData(objectList, date):
    objectList.clear()

    for index in range(24):
        entsoe = Entsoe()
                    
        entsoe.hour = index
        entsoe.date = str(date)[:10]
        entsoe.price = 0.0
        entsoe.euro = 1.0
        entsoe.status = False
        
        objectList.append(entsoe)





## łączy się z API entsoe i pobiera info o danym dniu
def getDataFromAPI_oneDay(date, errors, settings):
    try:
        country_code = 'PL'
        
        date_string = date.strftime("%Y-%m-%d")
        next_date = increaseOneDay(str(date_string)[:10].split('-'))
        next_date = str(next_date[0] + next_date[1] + next_date[2])

        client = EntsoeRawClient(api_key=settings.entsoeKey)
        start = pd.Timestamp(str(date_string), tz='Europe/Brussels')
        end = pd.Timestamp(str(next_date), tz='Europe/Brussels')

        apiAnswer = client.query_day_ahead_prices(country_code, start, end)
        
        return apiAnswer
    
    except Exception as e:
        ## jeśli napotka jakiś błąd (najpewniej brak danych dla podanego dnia) zwraca pusty string, co w funkcji 'parseENTSOE' przypisuje wartości '0' dla wszystkich godzin
        if date > datetime.datetime.now():   return ""
        elif "401 Client Error:" in str(e):   
            saveError("wrong entsoe key in parseENTSOE")
            print("Wrong entsoe key")
            return ""
        else:   
            print(f"An error occurred in parseENTSOE: {e}. Trying again")
            errors.entsoeErrorNumber += 1
            if errors.entsoeErrorNumber <= 5:   getDataFromAPI_oneDay(date, errors, settings)
            else:   return ""
            time.sleep(1)
        




## parsuje dane pobrane z entsoe
def parseENTSOE(date, objectList, errors, settings):
    errors.entsoeErrorNumber = 0
    try:
        internetConn = tryInternetConnection()
        if internetConn:
            objectList.clear()

            euro = getEUR(str(date)[:10].split('-'))
            string = getDataFromAPI_oneDay(date, errors, settings)

            if string == ""  or  string == None:
                resetData(objectList, date)
            else:
                document = parseString(string)

                if len(document.getElementsByTagName("price.amount")) != 24:   resetData(objectList, date)
                else:
                    for index in range(24):
                        entsoe = Entsoe()
                        price = document.getElementsByTagName("price.amount")[index].firstChild.nodeValue
                        date_fromapi = document.getElementsByTagName("end")[1].firstChild.nodeValue

                        entsoe.hour = index
                        entsoe.price = round(float(price) * euro, 2)
                        entsoe.date = date_fromapi[0:10]
                        entsoe.euro = euro
                        entsoe.status = True

                        objectList.append(entsoe)
            if internetConn:   print("entsoe parsed for: ", str(date)[0:10])
        else: 
            return


    except Exception as e:
        print(f"An error occurred in parseENTSOE: {e}. Trying again")
        saveError(str(e) + "  in parseENTSOE")
        errors.errorNumber += 1
        if errors.errorNumber <= 20:   parseENTSOE(date, objectList, errors, settings)
        else:   return
        time.sleep(1)
