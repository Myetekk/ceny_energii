import re
from urllib.request import urlopen






## pobiera dane o kursie euro w danym dniu
def getEUR(date):
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
    return float(eur)
    # return 4.28





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










## na podstawie nazwy kraju podaje jego kod 
def getCountryCode(value): 
    if value=='Bulgaria': country_code='BG'
    elif value=='Croatia': country_code='HR'
    elif value=='Czech Republic': country_code='CZ'
    elif value=='Denmark': country_code='DK_1'
    elif value=='Estonia': country_code='EE'
    elif value=='Finland': country_code='FI'
    elif value=='Greece': country_code='GR'
    elif value=='Hungary': country_code='HU'
    elif value=='Latwia': country_code='LV'
    elif value=='Lithuania': country_code='LT'
    elif value=='Montenegro': country_code='ME'
    elif value=='Netherlands': country_code='NL'
    elif value=='North Macedonia': country_code='MK'
    elif value=='Norway': country_code='NO_1'
    elif value=='Poland': country_code='PL'
    elif value=='Portugal': country_code='PT'
    elif value=='Romania': country_code='RO'
    elif value=='Serbia': country_code='RS'
    elif value=='Slovakia': country_code='SK'
    elif value=='Slovenia': country_code='SI'
    elif value=='Spain': country_code='ES'
    elif value=='Sweden': country_code='SE_1'
    elif value=='Switzerland': country_code='CH'
    return country_code


## na podstawie kodu kraju podaje jego nazwę 
def getCountryName(country_code):
    if country_code=='BG': country_code_temp='Bulgaria'
    elif country_code=='HR': country_code_temp='Croatia'
    elif country_code=='CZ': country_code_temp='Czech Republic'
    elif country_code=='DK_1': country_code_temp='Denmark'
    elif country_code=='EE': country_code_temp='Estonia'
    elif country_code=='FI': country_code_temp='Finland'
    elif country_code=='GR': country_code_temp='Greece'
    elif country_code=='HU': country_code_temp='Hungary'
    elif country_code=='LV': country_code_temp='Latwia'
    elif country_code=='LT': country_code_temp='Lithuania'
    elif country_code=='ME': country_code_temp='Montenegro'
    elif country_code=='NL': country_code_temp='Netherlands'
    elif country_code=='MK': country_code_temp='North Macedonia'
    elif country_code=='NO_1': country_code_temp='Norway'
    elif country_code=='PL': country_code_temp='Poland'
    elif country_code=='PT': country_code_temp='Portugal'
    elif country_code=='RO': country_code_temp='Romania'
    elif country_code=='RS': country_code_temp='Serbia'
    elif country_code=='SK': country_code_temp='Slovakia'
    elif country_code=='SI': country_code_temp='Slovenia'
    elif country_code=='ES': country_code_temp='Spain'
    elif country_code=='SE_1': country_code_temp='Sweden'
    elif country_code=='CH': country_code_temp='Switzerland'
    return country_code_temp










class PlotValues:
    value_entsoe = []
    value_entsoe_next = []
    value_tge = []
    value_tge_next = []
    value_diff = []
    value_diff_next = []



class PlotObj:
    fig = []
    canvas = []
    plot = []



class CheckboxStatus:
    entsoe_today_checked = True
    entsoe_tomorrow_checked = False
    tge_today_checked = True
    tge_tomorrow_checked = False
    diff_today_checked = False
    diff_tomorrow_checked = False



class Settings:
    currency = 'PLN'
    fixing = 1
    data_source = 1
    