import re
import time
import datetime
import copy
from urllib import request

from utils import getEUR, increaseOneDay, decreaseOneDay, decreaseOneMonth, saveError, tryInternetConnection





## klasa przechowująca dane zparsowane z TGE
class Tge:
    date = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
    hour = 0
    pricef1 = 0.0
    pricef2 = 0.0
    price = 0.0
    euro = 1.0
    currency = 'PLN'
    fixing = 1  ## 1-fixing pierwszy, 2-fixing drugi
    data_source = 2
    status = False  ## False- bad, True- good





def resetData(RDNList, euro): 
    RDNList.clear()
    
    for i in range(24):
        tge = Tge()
        tge.hour = i  
        tge.pricef1 = 0.0
        tge.pricef2 = 0.0
        tge.price = 0.0
        tge.euro = euro
        tge.status = False

        RDNList.append(tge)





## wyciąga dane z linijek i przypisuje do odpowiednich wartości
def getInfo(source_data, html_class_name, object, date, euro, settings):
    data_pattern = re.findall(html_class_name, source_data, re.DOTALL)

    if data_pattern != []: 
        for index in range(len(data_pattern)):
            data_pattern[index] = re.sub("<.*?>", "", data_pattern[index])
            data_pattern[index] = re.sub("\n", "", data_pattern[index], re.DOTALL)
            data_pattern[index] = re.sub("\\s", "", data_pattern[index])
            data_pattern[index] = data_pattern[index].replace(",", ".")

        object.date = date
        success = True

        try:
            object.pricef1 = round(float(data_pattern[0]), 2)
        except Exception as e:
            object.pricef1 = 0.0
            success = False

        try:
            object.pricef2 = round(float(data_pattern[2]), 2)
        except Exception as e:
            object.pricef2 = 0.0
            success = False
        

        if settings.fixing == 1:   object.price = object.pricef1
        elif settings.fixing == 2:   object.price = object.pricef2

        object.euro = euro
        object.status = True

        return {'success': success}





## parsuje dane pobrane z TGE
def parseTGE(date, RDNList, errors, settings):
    euro = 1

    try:
        if tryInternetConnection():
            RDNList.clear()

            euro = getEUR(str(date)[:10].split('-'))

            original_date = str(date)[:10]
            date = decreaseOneDay(str(date)[:10].split('-'))

            minimum_date = decreaseOneMonth(str(datetime.datetime.now())[:10].split('-'))
            minimum_date = decreaseOneMonth(minimum_date)
            minimum_date = increaseOneDay(minimum_date)

            original_date_ = original_date.split('-')
            original_date_ = datetime.datetime(int(original_date_[0]), int(original_date_[1]), int(original_date_[2]))
            minimum_date = datetime.datetime(int(minimum_date[0]), int(minimum_date[1]), int(minimum_date[2]))


            if original_date_ <= minimum_date: 
                ## gdy data jest zbyt daleko w tyle (TGE podaje dane tylko 2 mesiące wstacz)
                resetData(RDNList, euro)
            else:
                ## aby obejść (prawdopodobne) blokowanie przez strone zbyt częstych wejść
                inteager = 0
                while (True):
                    try:
                        ## tworzy odpowiedni link dla podanej daty
                        date_link = date[2] + "-" + date[1] + "-" + date[0]

                        url = "https://tge.pl/energia-elektryczna-rdn?dateShow=" + date_link + "&dateAction=prev"
                        page = request.urlopen(url, timeout=5)

                        ## czyta, dekoduje i znajduje wiersze w tabeli
                        html = page.read().decode(page.headers.get_content_charset()) 

                        ## sprawdza czy pobrane daty są dla porządanego dnia czy z jednego wcześniej
                        date_new = re.findall('<h4 class="kontrakt-date">.*?</h4>', html, re.DOTALL)
                        date_new = re.sub("<.*?>", "", date_new[0])
                        date_new = date_new.replace("Kontrakty godzinowe dla dostawy w dniu ", "")


                        prices = re.findall('<tbody.*?>.*?</tbody.*?>', html, re.DOTALL)
                        prices = re.findall('<tr.*?>.*?</tr.*?>', prices[2], re.DOTALL)
                        
                        
                        date_new_ = date_new.split('-')
                        date_link_ = date_link.split('-')
                        date_new_ = datetime.datetime(int(date_new_[2]), int(date_new_[1]), int(date_new_[0]))
                        date_link_ = datetime.datetime(int(date_link_[2]), int(date_link_[1]), int(date_link_[0])) + datetime.timedelta(days=1)


                        if date_new == date_link  or  date_link_ >= ( datetime.datetime.now() + datetime.timedelta(days=1) ):
                            resetData(RDNList, euro)
                        else:
                            ## wyciąga pojedyńcze dane z wierszy tabeli
                            hourIndex = 0
                            for price in prices:
                                tge = Tge()
                                result = getInfo(price, '<td style="display: table-cell;" class="footable-visible.*?>.*?</td.*?>', tge, original_date, euro, settings)  ## wartości
                                tge.hour = hourIndex

                                if (len(prices) == 25  and hourIndex == 2): # gdy lista ma 25 obiektów  =>  zmiana czasu z letniego na zimowy
                                    print('TGE za dużo godzin w dobie')
                                elif (len(prices) == 23  and hourIndex == 2): # gdy lista ma 25 obiektów  =>  zmiana czasu z letniego na zimowy
                                    print('TGE za mało godzin w dobie')
                                    RDNList.append(copy.deepcopy(tge))
                                    RDNList.append(copy.deepcopy(tge))
                                elif (result["success"] == True  or  (result["success"] == False  and  len(prices) == 24)): ## gdy dobra wartość lub gdy zła wartość ale to nie zmiana czasu
                                    RDNList.append(tge)
                                hourIndex += 1
                        break

                    except Exception as e:
                        print(f"An error occurred in parseTGE (inner): {e}. Trying again")
                        time.sleep(1)
                        inteager += 1
                        if inteager > 10:  ## jeśli zbyt dużo razy nie udało mu się pobrać danych - ustawia 0 
                            resetData(RDNList, euro)
                            break
            print("tge parsed for: ", original_date)
        else: 
            return


    except Exception as e:
        print(f"An error occurred in parseTGE: {e}. Trying again")
        saveError(str(e) + "  in parseTGE")
        errors.errorNumber += 1
        if errors.errorNumber <= 20:   parseTGE(date, RDNList, errors, settings)
        else:   
            resetData(RDNList, euro)
            return
        time.sleep(1)
