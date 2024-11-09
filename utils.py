import tkinter as tk
from tkinter import BOTH
import re
import os
import sqlite3
import datetime
from urllib import request

from settingsOperations import saveSettings_JSON





## pobiera dane o kursie euro w danym dniu
def getEUR(date): 
    date_prev_start = decreaseOneDay(date)
    date_prev_end = decreaseOneDay(date_prev_start)
    date_prev_end = decreaseOneDay(date_prev_end)
    date_prev_end = decreaseOneDay(date_prev_end)
    date_prev_start = date_prev_start[0] + "-" + date_prev_start[1] + "-" + date_prev_start[2]
    date_prev_end = date_prev_end[0] + "-" + date_prev_end[1] + "-" + date_prev_end[2]

    url = "https://www.money.pl/pieniadze/nbparch/srednie/?symbol=EUR.n&from=" + date_prev_end + "&to=" + date_prev_start
    page = request.urlopen(url)
    html = page.read().decode("utf-8")

    html_class_name = """<div class="rt-td" role="gridcell".*?><div style="text-align:right">.*?</div></div>"""
    eur = re.findall(html_class_name, html, re.DOTALL)
    eur = re.sub('</div></div>', "", eur[0])
    eur = re.sub('<.*>', "", eur)
    eur = re.sub(',', ".", eur)

    return float(eur)










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










## sprawdza ilość errorów i jeśli trzeba to restartuje apke
def checkNumberOfErrors(errors, settings, window):
    if errors.errorNumber >= 20:
        print('Too much errors  \n\nRestarting app\n\n')
        saveSettings_JSON(settings, errors)
        if window != None:   window.destroy()





## sprawdza czy ma połączenie z internetem
def tryInternetConnection():
    try:
        request.urlopen('https://www.google.com', timeout=5)
        return True
    
    except request.URLError as err: 
        print('no internet connection')
        saveError('  no internet connection')
        return False





## tworzy okienko z podaną wiadomością i przyciskiem do zamknięcia
def errorWindow(message, windowTitle):
    print(message)
    errorWindow = tk.Tk()
    errorWindow.title(windowTitle)
    errorWindow.resizable(False, False)
    errorWindow.geometry("+500+500")
    errorWindow.configure(background='#bfbfbf')
    tk.Label(errorWindow, text=message, font='Helvetica 16').pack(fill=BOTH, padx=40, pady=10)
    tk.Button(errorWindow, text="ok", command=errorWindow.destroy, font='20').pack(padx=50, pady=(10, 15))
    errorWindow.mainloop()





## loguje błędy do pliku .txt
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










## status zaznaczenia checkboxów odpowiadających za wykres
class CheckboxStatus:
    entsoe_today_checked = True
    entsoe_tomorrow_checked = False
    tge_today_checked = True
    tge_tomorrow_checked = False
    diff_today_checked = False
    diff_tomorrow_checked = False



## ustawienia aplikacji, zapisują się w pliku .json, a w czasie pracy aplikacji są wysyłane modbusem
class Settings:
    currency = 'PLN'  ## waluta - PLN / EUR
    fixing = 2  ## 1- fixing I, 2- fixing II
    data_source = 1  ## 1- entsoe, 2- tge
    updateTime = 15  ## w sekundach
    entsoeKey = 'd2f433b7-ab33-4210-8328-15b9462f7316'  ## klucz do api entsoe
    


## informacje o ilośći errorów
class Errors:
    errorNumber = 0  ## ilość errorów
    entsoeErrorNumber = 0  ## ilosć errorów w entsoe
