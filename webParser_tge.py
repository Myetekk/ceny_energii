import re
import time
import datetime
from urllib.request import urlopen

from utils import getEUR, increaseOneDay, decreaseOneDay, decreaseOneMonth, checkNumberOfErrors





## klasa przechowująca dane zparsowane z TGE
class Tge:
    date = datetime.datetime(2024, 7, 1)
    hour = 0
    pricef1 = 0.0
    pricef2 = 0.0
    price = 0.0
    euro = 1
    currency = 'PLN'
    fixing = 1  ## 1-fixing pierwszy, 2-fixing drugi
    data_source = 2
    

    def printProps(self):
        print(self.date, ', ', self.hour, ", ", self.pricef1, ", ", self.pricef2, ", ", self.price, ", ", self.euro, ", ", self.currency, ", ", self.fixing, ", ", self.data_source)





## wyciąga dane z linijek i przypisuje do odpowiednich wartości
def getInfo(source_data, html_class_name, object, type_of_data, date, euro):
    data_pattern = re.findall(html_class_name, source_data, re.DOTALL)

    if data_pattern != []: 
        for index in range(len(data_pattern)):
            data_pattern[index] = re.sub("<.*?>", "", data_pattern[index])
            data_pattern[index] = re.sub("\n", "", data_pattern[index], re.DOTALL)
            data_pattern[index] = re.sub("\\s", "", data_pattern[index])
            data_pattern[index] = data_pattern[index].replace(",", ".")

        if type_of_data=="time": object.hour = data_pattern[0]
        elif type_of_data=="rate": 
            object.date = date
            object.pricef1 = round(float(data_pattern[0]), 2)
            object.pricef2 = round(float(data_pattern[2]), 2)
            object.price = round(float(data_pattern[0]), 2)
            object.euro = euro





## parsuje dane pobrane z TGE
def parseTGE(date, RDNList, errors, settings, window):
    try:
        RDNList.clear()

        euro = getEUR(str(date)[:10].split('-'), errors, settings, window)

        original_date = str(date)[:10]
        date = decreaseOneDay(str(date)[:10].split('-'))

        minimum_date = decreaseOneMonth(str(datetime.datetime.now())[:10].split('-'))
        minimum_date = decreaseOneMonth(minimum_date)
        minimum_date = increaseOneDay(minimum_date)

        original_date_ = original_date.split('-')
        original_date_ = datetime.datetime(int(original_date_[0]), int(original_date_[1]), int(original_date_[2]))
        minimum_date = datetime.datetime(int(minimum_date[0]), int(minimum_date[1]), int(minimum_date[2]))


        if original_date_ <= minimum_date: 
            ## gdy data jest zbyt daleko w tyle (TGE podaje dane tylko 3 mesiące wstacz)
            for i in range(24):
                tge = Tge()
                tge.hour = -1  
                tge.pricef1 = 0.0
                tge.pricef2 = 0.0
                tge.price = 0.0
                tge.euro = euro

                RDNList.append(tge)
        else:
            ## aby obejść (prawdopodobne) blokowanie przez strone zbyt częstych wejść
            inteager = 0
            while(True):
                try:
                    ## tworzy odpowiedni link dla podanej daty
                    date_link = date[2] + "-" + date[1] + "-" + date[0]

                    url = "https://tge.pl/energia-elektryczna-rdn?dateShow=" + date_link + "&dateAction=prev"
                    page = urlopen(url, timeout=5)

                    ## czyta, dekoduje i znajduje wiersze w tabeli
                    html = page.read().decode(page.headers.get_content_charset()) 

                    ## sprawdza czy pobrane daty są dla porządanego dnia czy z jednego wcześniej
                    date_new = re.findall('<h4 class="kontrakt-date">.*?</h4>', html, re.DOTALL)
                    date_new = re.sub("<.*?>", "", date_new[0])
                    date_new = date_new.replace("Kontrakty godzinowe dla dostawy w dniu ", "")


                    prices = re.findall('<tbody.*?>.*?</tbody.*?>', html, re.DOTALL)
                    prices = re.findall('<tr.*?>.*?</tr.*?>', prices[2], re.DOTALL)

                    ## wyciąga pojedyńcze dane z wierszy tabeli
                    for price in prices:
                        tge = Tge()
                        getInfo(price, '<td.*?class="footable-visible footable-first-column.*?">.*?</td.*?>', tge, "time", original_date, euro)  ## godziny
                        getInfo(price, '<td style="display: table-cell;" class="footable-visible.*?>.*?</td.*?>', tge, "rate", original_date, euro)  ## wartości
                        
                        if date_new == date_link:
                            tge.date = original_date
                            tge.hour = -1
                            tge.pricef1 = 0.0
                            tge.pricef2 = 0.0
                            tge.price = 0.0
                            tge.euro = euro
                        if tge.hour != 0:
                            RDNList.append(tge)
                    break

                except Exception as e:
                    print(f"An error occurred in parseTGE (inner): {e}. Trying again")
                    time.sleep(1)
                    inteager += 1
                    if inteager > 10:  ## jeśli zbyt dużo razy nie udało mu się pobrać danych - ustawia 0 
                        for i in range(24):
                            tge = Tge()
                            tge.date = original_date
                            tge.hour = -1
                            tge.pricef1 = 0.0
                            tge.pricef2 = 0.0
                            tge.price = 0.0
                            tge.euro = euro

                            RDNList.append(tge)
                        break
            print("tge parsed")

    except Exception as e:
        print(f"An error occurred in parseTGE: {e}. Trying again")
        errors.errorNumber += 1
        if errors.errorNumber <= 20:   parseTGE(date, RDNList, errors, settings, window)
        else:   return
        time.sleep(1)
