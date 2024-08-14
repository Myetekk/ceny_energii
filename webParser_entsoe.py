import pandas as pd
import time
from entsoe import EntsoeRawClient
import datetime
from xml.dom.minidom import parseString

from utils import getEUR, increaseOneDay, checkNumberOfErrors





## klasa przechowująca dane zparsowane z entsoe
class Entsoe:
    date = datetime.datetime(2024, 7, 1)
    hour = 0
    price = 0
    euro = 1
    currency = 'PLN'
    fixing = 1  ## dla entsoe tylko fixing pierwszy
    data_source = 1

    def printProps(self):
        print(self.hour, ", ", self.price, ", ", self.date)





## łączy się z API entsoe i pobiera info o danym dniu
def getDataFromAPI_oneDay(date):
    try:
        country_code = 'PL'
        
        date_string = date.strftime("%Y-%m-%d")
        next_date = increaseOneDay(str(date_string)[:10].split('-'))
        next_date = str(next_date[0] + next_date[1] + next_date[2])

        client = EntsoeRawClient(api_key='d2f433b7-ab33-4210-8328-15b9462f7316')
        start = pd.Timestamp(str(date_string), tz='Europe/Brussels')
        end = pd.Timestamp(str(next_date), tz='Europe/Brussels')

        apiAnswer = client.query_day_ahead_prices(country_code, start, end)
        return apiAnswer
    
    except:
        ## jeśli napotka jakiś błąd (najpewniej brak danych dla podanego dnia) zwraca pusty string, co w funkcji 'parseENTSOE' przypisuje wartości '0' dla wszystkich godzin
        return ""
        




## parsuje dane pobrane z entsoe
def parseENTSOE(date, objectList, errors, settings, window):
    euro = getEUR(str(date)[:10].split('-'), errors, settings, window)
    
    string = getDataFromAPI_oneDay(date)
    

    try:
        objectList.clear()

        if string=="":
            for index in range(24): 
                entsoe = Entsoe()
                
                entsoe.hour = index
                entsoe.price = 0.0
                entsoe.date = str(date)[0:10]
                entsoe.euro = euro
                
                objectList.insert(len(objectList), entsoe)
        else:
            document = parseString(string)

            for index in range(24):
                entsoe = Entsoe()
                price = document.getElementsByTagName("price.amount")[index].firstChild.nodeValue
                date = document.getElementsByTagName("end")[1].firstChild.nodeValue

                entsoe.hour = index
                entsoe.price = round(float(price) * euro, 2)
                entsoe.date = date[0:10]
                entsoe.euro = euro

                objectList.insert(len(objectList), entsoe)
        print("entsoe parsed")

    except Exception as e:
        print(f"An error occurred in parseENTSOE: {e}. Trying again")
        errors.errorNumber += 1
        if errors.errorNumber <= 20:   parseENTSOE(date, objectList, errors, settings, window)
        else:   return
        time.sleep(1)
