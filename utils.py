import re
import time
from urllib.request import urlopen

from settingsOperations import saveSettings_JSON





## pobiera dane o kursie euro w danym dniu
def getEUR(date, errors, settings, window): 
    # try:
        date_prev_start = decreaseOneDay(date)
        date_prev_end = decreaseOneDay(date_prev_start)
        date_prev_end = decreaseOneDay(date_prev_end)
        date_prev_end = decreaseOneDay(date_prev_end)
        date_prev_start = date_prev_start[0] + "-" + date_prev_start[1] + "-" + date_prev_start[2]
        date_prev_end = date_prev_end[0] + "-" + date_prev_end[1] + "-" + date_prev_end[2]

        url = "https://www.money.pl/pieniadze/nbparch/srednie/?symbol=EUR.n&from=" + date_prev_end + "&to=" + date_prev_start
        page = urlopen(url)
        html = page.read().decode("utf-8")

        html_class_name = """<div class="rt-td" role="gridcell".*?><div style="text-align:right">.*?</div></div>"""
        eur = re.findall(html_class_name, html, re.DOTALL)
        eur = re.sub('</div></div>', "", eur[0])
        eur = re.sub('<.*>', "", eur)
        eur = re.sub(',', ".", eur)

        # print(float(eur))
        # raise Exception("TESTING")
    
        return float(eur)

    # except Exception as e:
    #     print(f"An error occurred in getEUR: {e}. Trying again")
    #     errors.errorNumber += 1
    #     if errors.errorNumber <= 20:   getEUR(date, errors, settings, window)
    #     else:   checkNumberOfErrors(errors, settings, window)
    #     time.sleep(1)




## zwraca podaną date zmniejszoną o jeden dzień
def decreaseOneDay(date_data):
    year = str(date_data[0])
    month = str(date_data[1])
    day = str(date_data[2])

    if (day=='01' and (month=='02' or month=='04' or month=='06' or month=='08' or month=='09' or month=='11')):
        ##  przejście na poprzedni miesiąc, gdy 31 dni
        day = '31'
        month = int(month) - 1
        if (len(str(month))==1): month = '0' + str(month)
    elif (day=='01' and (month=='05' or month=='07' or month=='10' or month=='12')):
        ##  przejście na poprzedni miesiąc, gdy 30 dni
        day = '30'
        month = int(month) - 1
        if (len(str(month))==1): month = '0' + str(month)
    elif (day=='01' and month=='03'):
        ##  przejście na poprzedni miesiąc, ale to luty
        if int(year)%4 == 0: day = '29'
        else: day = '28'
        month = int(month) - 1        
    elif (day=='01' and month=='01'):
        ##  przejśćie w stary rok
        day = '31'
        month = '12'
        year = int(year) - 1
    else:
        ##  przejście w poprzedni dzień
        day = int(day) - 1
        if (len(str(day))==1): day = '0' + str(day)
    prev_day = [str(year), str(month), str(day)]
    return prev_day


## zwraca podaną date zwiększoną o jeden dzień
def increaseOneDay(date_data):
    year = str(date_data[0])
    month = str(date_data[1])
    day = str(date_data[2])

    if (day=='30' and (month=='04' or month=='06' or month=='09' or month=='11')) or (day=='31' and (month=='01' or month=='03' or month=='05' or month=='07' or month=='08' or month=='10')) or (( (day=='28' and int(year)%4!=0) or (day=='29' and int(year)%4==0)) and month=='02'):
        ##  przejście na następny miesiąc
        day = '01'
        month = int(month) + 1
        if (len(str(month))==1): month = '0' + str(month)
    elif (day=='31' and month=='12'):
        ##  przejśćie w nowy rok
        day = '01'
        month = '01'
        year = int(year) + 1
    else:
        ##  przejście w nowy dzień
        day = int(day) + 1
        if (len(str(day))==1): day = '0' + str(day)
    next_day = [str(year), str(month), str(day)]
    return next_day


## zwraca podaną date zmniejszoną o jeden miesiąc
def decreaseOneMonth(date_data):
    year = str(date_data[0])
    month = str(date_data[1])
    day = str(date_data[2])

    if (day=='31' and (month=='05' or month=='07' or month=='10' or month=='12')):
        ##  przejście na poprzedni miesiąc, gdy 30 dni
        day = '30'
        month = int(month) - 1
        if (len(str(month))==1): month = '0' + str(month)
    elif ((day=='31' or day=='30' or day=='29') and month=='03'):
        ##  przejście na poprzedni miesiąc, ale to luty
        if int(year)%4 == 0: day = '29'
        else: day = '28'
        month = int(month) - 1        
    elif (month=='01'):
        ##  przejśćie w stary rok
        month = '12'
        year = int(year) - 1
    else:
        ##  przejście w poprzedni miesiąc
        month = int(month) - 1
        if (len(str(month))==1): month = '0' + str(month)
    prev_day = [str(year), str(month), str(day)]
    return prev_day


## zwraca podaną date zwiększoną o jeden miesiąc
def increaseOneMonth(date_data):
    year = str(date_data[0])
    month = str(date_data[1])
    day = str(date_data[2])

    if (day=='31' and (month=='03' or month=='05' or month=='8' or month=='10')):
        ##  przejście na poprzedni miesiąc, gdy 30 dni
        day = '30'
        month = int(month) + 1
        if (len(str(month))==1): month = '0' + str(month)
    elif ((day=='31' or day=='30' or day=='29') and month=='01'):
        ##  przejście na poprzedni miesiąc, ale to luty
        if int(year)%4 == 0: day = '29'
        else: day = '28'
        month = int(month) + 1  
    elif (month=='12'):
        ##  przejśćie w nowy rok
        month = '01'
        year = int(year) + 1
    else:
        ##  przejście na następny miesiąc
        month = int(month) + 1
        if (len(str(month))==1): month = '0' + str(month)        
    next_day = [str(year), str(month), str(day)]
    return next_day










def checkNumberOfErrors(errors, settings, window):
    if errors.errorNumber >= 20:
        print('Too much errors  \n\nRestarting app\n\n')
        saveSettings_JSON(settings, errors)
        if window != None:   window.destroy()









class PlotValues:
    value_entsoe = None
    value_entsoe_next = None
    value_tge = None
    value_tge_next = None
    value_diff = None
    value_diff_next = None



class PlotObj:
    fig = None
    canvas = None
    plot = None



class CheckboxStatus:
    entsoe_today_checked = True
    entsoe_tomorrow_checked = False
    tge_today_checked = True
    tge_tomorrow_checked = False
    diff_today_checked = False
    diff_tomorrow_checked = False



class Settings:
    currency = 'PLN'
    fixing = 2
    data_source = 1
    


class Errors:
    errorNumber = 0