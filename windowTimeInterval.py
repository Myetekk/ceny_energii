import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
import threading
import datetime
import pandas
import time
import csv
import json
import os
import babel.numbers

from webParser_entsoe import parseENTSOE
from webParser_tge import parseTGE
from utils import Settings, Errors, errorWindow, saveError, tryInternetConnection





class EnergyPrices_timeInterval:
    window = None
    frame_table = None
    frame_header = None

    
    # date_start = (datetime.datetime.now() - datetime.timedelta(days=1))
    date_start = datetime.datetime.now()
    date_stop = datetime.datetime.now() + datetime.timedelta(days=1)

    CalendarStart = None
    CalendarStop = None
    dataList = list()





    ## ładuje nagłówek z wybieraniem przedziału czasu
    def loadHeader(self):
        def calendar_onChange():
            if tryInternetConnection():
                self.date_start = self.CalendarStart.get_date()
                self.date_stop = self.CalendarStop.get_date()

                
                if self.date_start <= self.date_stop  and  (self.date_stop-self.date_start).days <= 120:   
                    self.getData()
                elif (self.date_stop-self.date_start).days > 120:   errorWindow('przedział to maksymalnie 120 dni', 'error')
                else:   errorWindow('nieprawidłowa data', 'error')
            else:   errorWindow('no internet connection', 'error')

        
        self.CalendarStart_variable = tk.StringVar()
        self.CalendarStop_variable = tk.StringVar()
        
        CalendarStart_frame = tk.Frame(self.frame_header, background='#e6f2ec')
        CalendarStop_frame = tk.Frame(self.frame_header, background='#e6f2ec')

        self.CalendarStart = DateEntry(CalendarStart_frame, textvariable=self.CalendarStart_variable, width=11, year=self.date_start.year, month=self.date_start.month, day=self.date_start.day, background='darkblue', foreground='white', date_pattern='yyyy-MM-dd', state='readonly')
        self.CalendarStop = DateEntry(CalendarStop_frame, textvariable=self.CalendarStop_variable, width=11, year=self.date_stop.year, month=self.date_stop.month, day=self.date_stop.day, background='darkblue', foreground='white', date_pattern='yyyy-MM-dd', state='readonly')

        self.CalendarStart.pack(side=RIGHT, pady=20)
        self.CalendarStop.pack(side=RIGHT, pady=20)

        tk.Label(CalendarStart_frame, text="od  ", background='#e6f2ec').pack(side=LEFT, pady=20)
        tk.Label(CalendarStop_frame, text="do  ", background='#e6f2ec').pack(side=LEFT, pady=20)

        CalendarStart_frame.pack()
        CalendarStop_frame.pack()


        tk.Button(self.frame_header, text=' RELOAD', command=calendar_onChange).pack(pady=(20, 50), ipadx=3, ipady=3)



        ## wybieranie waluty
        def currencySelected():
            if self.dataList[0].objectList_tge[0].currency != self.currencyStringVar.get():
                self.settings.currency = self.currencyStringVar.get()
                self.changeCurrency()
            self.reloadElements()
        self.currencyStringVar = tk.StringVar(self.frame_header, self.settings.currency)
        currencyFrame = tk.Frame(self.frame_header, background='#e6f2ec')
        tk.Label(currencyFrame, text="waluta:", background='#e6f2ec').pack(side='top', padx=5)
        tk.Radiobutton(currencyFrame, text='PLN', variable=self.currencyStringVar, value='PLN', command=currencySelected, background='#e6f2ec').pack(side='top', padx=5)
        tk.Radiobutton(currencyFrame, text='EUR', variable=self.currencyStringVar, value='EUR', command=currencySelected, background='#e6f2ec').pack(side='bottom', padx=5)
        currencyFrame.pack(pady=(5, 10))


        ## wybieranie fixingu
        def fixingSelected():
            self.settings.fixing = self.fixingStringVar.get()
            self.changeFixing()
            if self.dataList[0].objectList_tge[0].currency != self.currencyStringVar.get():
                self.settings.currency = self.currencyStringVar.get()
                self.changeCurrency()
            self.reloadElements()
        self.fixingStringVar = tk.StringVar(self.frame_header, self.settings.fixing)
        fixingFrame = tk.Frame(self.frame_header, background='#e6f2ec')
        tk.Label(fixingFrame, text="fixing tge:", background='#e6f2ec').pack(side='top', padx=5)
        tk.Radiobutton(fixingFrame, text='fixing 1', variable=self.fixingStringVar, value='1', command=fixingSelected, background='#e6f2ec').pack(side='top', padx=5)
        tk.Radiobutton(fixingFrame, text='fixing 2', variable=self.fixingStringVar, value='2', command=fixingSelected, background='#e6f2ec').pack(side='bottom', padx=5)
        fixingFrame.pack(pady=(5, 50))



        tk.Button(self.frame_header, text='JSON', command=self.exportToJSON).pack(pady=(5, 10), ipadx=3, ipady=3)
        tk.Button(self.frame_header, text='CSV', command=self.exportToCSV).pack(pady=(10, 50), ipadx=3, ipady=3)
        


        self.frame_header.pack(side=LEFT, anchor=N, padx=(0, 15))

    



    ## przeładowuje elementy zapisane w pamięci
    def reloadElements(self):
        for widget in self.frame_table.winfo_children(): widget.destroy() 


        self.canvas = tk.Canvas(self.frame_table, background='#dae6e0')
        self.scrollbar = ttk.Scrollbar(self.frame_table, orient="horizontal")
        self.scrollable_frame = tk.Frame(self.canvas, background='#dae6e0')

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure( scrollregion=self.canvas.bbox("all") ))
        self.canvas.create_window((0, 0), window=self.scrollable_frame)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)


        ## wizualizuje dane dla kazdego dnia
        for index in range(len(self.dataList), 0, -1):
            self.loadOneDay(index-1)
        

        self.canvas.xview_moveto(0.0)
        self.scrollbar.configure(command=self.canvas.xview)
        self.scrollbar.pack(side=BOTTOM, fill=X)
        self.canvas.pack(side=TOP, fill=BOTH, expand=True)
        self.frame_table.pack(side=RIGHT, fill=BOTH, expand=1)





    ## ładuje dane z bazy danych, w tym czasie pokazuje loading screan
    def getData(self):
        try:
            print('\n\nLoading combinedData window..')

            for widget in self.frame_table.winfo_children(): widget.destroy() 
            
            tk.Label(self.frame_table, text='Loading..', font='Helvetica 14', background='#e6f2ec').pack()
            self.frame_table.pack()

            ## tworzy listę dat i dla każdej z nich pobiera dane
            self.dataList.clear()
            self.datelist = pandas.date_range(self.date_start, self.date_stop)
            for date in self.datelist: 
                oneDayObject = OneDayObject()
                parse_entsoe_thread = threading.Thread(target=parseENTSOE, args=(date, oneDayObject.objectList_entsoe, self.errors, self.settings, ), daemon = True)
                parse_tge_thread = threading.Thread(target=parseTGE, args=(date, oneDayObject.objectList_tge, self.errors, self.settings, ), daemon = True)

                parse_entsoe_thread.start()
                parse_tge_thread.start()

                parse_entsoe_thread.join()
                parse_tge_thread.join()

                print('\n')

                self.dataList.append(oneDayObject.copy())


            for widget in self.frame_table.winfo_children(): widget.destroy() 


            self.canvas = tk.Canvas(self.frame_table, background='#dae6e0')
            self.scrollbar = ttk.Scrollbar(self.frame_table, orient="horizontal")
            self.scrollable_frame = tk.Frame(self.canvas, background='#dae6e0')

            self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure( scrollregion=self.canvas.bbox("all") ))
            self.canvas.create_window((0, 0), window=self.scrollable_frame)
            self.canvas.configure(xscrollcommand=self.scrollbar.set)


            ## zmienia walute jeśli potrzebne
            if self.dataList[0].objectList_tge[0].currency != self.currencyStringVar.get():
                self.settings.currency = self.currencyStringVar.get()
                self.changeCurrency()
            
            ## zmienia fixing jeśli potrzebne
            if self.dataList[0].objectList_tge[0].fixing != self.settings.fixing:   
                self.settings.fixing = self.fixingStringVar.get()
                self.changeFixing()


            ## wizualizuje dane dla kazdego dnia
            for index in range(len(self.dataList), 0, -1):
                self.loadOneDay(index-1)
            

            self.canvas.xview_moveto(0.0)
            self.scrollbar.configure(command=self.canvas.xview)
            self.scrollbar.pack(side=BOTTOM, fill=X)
            self.canvas.pack(side=TOP, fill=BOTH, expand=True)
            self.frame_table.pack(side=RIGHT, fill=BOTH, expand=1)

            print('Loaded combinedData window')

        except Exception as e:
            print(f"An error occurred in GetData in combinedData: {e}.")
            saveError(str(e) + "  in GetData in combinedData")
            self.errors.errorNumber += 1
            if self.errors.errorNumber <= 10: 
                self.getData()
            else:   
                self.restartWindow()





    ## ładuje dane w formie tabelki
    def loadOneDay(self, index):
        self.frame_table_inner = tk.Frame(self.scrollable_frame, background='#666666')
        
        headerBackground = '#cccccc'
        tk.Label(self.frame_table_inner, text=(self.dataList[index].objectList_entsoe[0].date), font='Helvetica 10', background=headerBackground).grid(row=0, column=0, padx=1, pady=1, ipadx=2, ipady=2, sticky=NSEW)
        tk.Label(self.frame_table_inner, text='entsoe', font='Helvetica 10 bold', background=headerBackground, width=5).grid(row=0, column=1, padx=1, pady=1, ipadx=2, ipady=2, sticky=NSEW)
        tk.Label(self.frame_table_inner, text='tge', font='Helvetica 10 bold', background=headerBackground, width=5).grid(row=0, column=3, padx=1, pady=1, ipadx=2, ipady=2, sticky=NSEW)


        self.backgroundColor = '#d9cece'
        for i in range(24):
            if i%2 == 0:   self.backgroundColor = '#d4d9ce'
            else:   self.backgroundColor = '#d9cece'
            
            tk.Label(self.frame_table_inner, text=str(self.dataList[index].objectList_entsoe[i].hour)[:2], font='Helvetica 11 bold', background=self.backgroundColor).grid(row=i+1, column=0, padx=1, pady=1, ipadx=2, ipady=2, sticky=NSEW)
            tk.Label(self.frame_table_inner, text=round(self.dataList[index].objectList_entsoe[i].price, 2), font='Helvetica 10', background=self.backgroundColor).grid(row=i+1, column=1, padx=1, pady=1, ipadx=2, ipady=2, sticky=NSEW)
            tk.Label(self.frame_table_inner, text=round(self.dataList[index].objectList_tge[i].price, 2), font='Helvetica 10', background=self.backgroundColor).grid(row=i+1, column=3, padx=1, pady=1, ipadx=2, ipady=2, sticky=NSEW)

        self.frame_table_inner.pack(side=RIGHT, fill=BOTH, expand=1, padx=10, pady=10)





    ## tworzy cały interfejs
    def createInterface(self, combinedDataButton):
        self.window = tk.Tk()
        self.window.title('Energy prices - combined data')
        self.window.geometry('1200x810+50+50')
        self.window.resizable(False, False)
        self.window.configure(padx=10, pady=10)
        self.window.configure(background='#e6f2ec')
        
        self.frame_table = tk.Frame(self.window, background='#e6f2ec')
        self.frame_header = tk.Frame(self.window, background='#e6f2ec')


        self.errors = Errors()
        self.settings = Settings()

        self.combinedDataButton = combinedDataButton
        self.combinedDataButton.configure(state='disabled')

        self.loadHeader()


        gatData_thread = threading.Thread(target=self.getData, daemon=True)
        gatData_thread.start()

        
        self.window.protocol("WM_DELETE_WINDOW", self.closeWindow)
        self.window.mainloop()
    




    ## zmienia walute danych
    def changeCurrency(self):
        multiply = 1
        if self.settings.currency == 'EUR':
            for index in range(len(self.dataList), 0, -1):
                multiply = self.dataList[index-1].objectList_entsoe[0].euro
                for i in range(24):
                    self.dataList[index-1].objectList_entsoe[i].price = float(self.dataList[index-1].objectList_entsoe[i].price) / multiply
                    self.dataList[index-1].objectList_tge[i].price = float(self.dataList[index-1].objectList_tge[i].price) / multiply

                    self.dataList[index-1].objectList_entsoe[i].currency = 'EUR'
                    self.dataList[index-1].objectList_tge[i].currency = 'EUR'
        elif self.settings.currency == 'PLN':
            for index in range(len(self.dataList), 0, -1):
                multiply = 1 / self.dataList[index-1].objectList_entsoe[0].euro
                for i in range(24):
                    self.dataList[index-1].objectList_entsoe[i].price = float(self.dataList[index-1].objectList_entsoe[i].price) / multiply
                    self.dataList[index-1].objectList_tge[i].price = float(self.dataList[index-1].objectList_tge[i].price) / multiply
                    
                    self.dataList[index-1].objectList_entsoe[i].currency = 'PLN'
                    self.dataList[index-1].objectList_tge[i].currency = 'PLN'





    ## zmienia fixing dla tge
    def changeFixing(self):
        if str(self.settings.fixing) == '1':
            for index in range(len(self.dataList), 0, -1):
                for i in range(24):
                    self.dataList[index-1].objectList_tge[i].price = float(self.dataList[index-1].objectList_tge[i].pricef1)
                    self.dataList[index-1].objectList_tge[i].currency = 'PLN'
                    self.dataList[index-1].objectList_tge[i].fixing = 1
        elif str(self.settings.fixing) == '2': 
            for index in range(len(self.dataList), 0, -1):
                for i in range(24):
                    self.dataList[index-1].objectList_tge[i].price = float(self.dataList[index-1].objectList_tge[i].pricef2)
                    self.dataList[index-1].objectList_tge[i].currency = 'PLN'
                    self.dataList[index-1].objectList_tge[i].fixing = 2
        
        if self.dataList[0].objectList_tge[i].currency != self.settings.currency:
            multiply = 1
            if self.settings.currency == 'EUR':
                for index in range(len(self.dataList), 0, -1):
                    multiply = self.dataList[0].objectList_tge[0].euro
                    for i in range(24):
                        self.dataList[index-1].objectList_tge[i].price = float(self.dataList[index-1].objectList_tge[i].price) / multiply
                        self.dataList[index-1].objectList_tge[i].currency = 'EUR'
            elif self.settings.currency == 'PLN':
                for index in range(len(self.dataList), 0, -1):
                    multiply = 1 / self.dataList[0].objectList_tge[0].euro
                    for i in range(24):
                        self.dataList[index-1].objectList_tge[i].price = float(self.dataList[index-1].objectList_tge[i].price) / multiply
                        self.dataList[index-1].objectList_tge[i].currency = 'PLN'





    ## tworzy plik CSV z danymi
    def exportToCSV(self):
        try:
            if os.path.exists("outputs") == False: os.mkdir("outputs") 
            if os.path.exists("outputs\\" + str(self.date_start)[:10] + "__" + str(self.date_stop)[:10]) == False: os.mkdir("outputs\\" + str(self.date_start)[:10] + "__" + str(self.date_stop)[:10]) 
            fileName = "outputs\\" + str(self.date_start)[:10] + "__" + str(self.date_stop)[:10] + '\\' + str(self.date_start)[:10] + "__" + str(self.date_stop)[:10] + ".csv"

            with open(fileName, "w", newline='') as file:
                writer = csv.writer(file)
                
                writer.writerow(["date", "hour", "entsoe", "tge"])
                for obj in self.dataList:
                    for i in range(24):
                        writer.writerow([obj.objectList_entsoe[i].date, obj.objectList_entsoe[i].hour, round(obj.objectList_entsoe[i].price, 2), round(obj.objectList_tge[i].price, 2)])

        except Exception as e:
            print(f"An error occurred in exportToCSV in combinedData: {e}.")
            saveError(str(e) + "  in exportToCSV in combinedData")
            self.errors.errorNumber += 1
            if self.errors.errorNumber <= 10: 
                self.exportToCSV()
            else:   
                self.restartWindow()
    




    ## tworzy plik JSON z danymi
    def exportToJSON(self):
        try:
            if os.path.exists("outputs") == False: os.mkdir("outputs") 
            if os.path.exists("outputs\\" + str(self.date_start)[:10] + "__" + str(self.date_stop)[:10]) == False: os.mkdir("outputs\\" + str(self.date_start)[:10] + "__" + str(self.date_stop)[:10]) 
            fileName = "outputs\\" + str(self.date_start)[:10] + "__" + str(self.date_stop)[:10] + '\\' + str(self.date_start)[:10] + "__" + str(self.date_stop)[:10] + ".json"

            with open(fileName, "w", newline='') as file:
                file.write('[\n\n')
                
                index = 0
                for obj in self.dataList:
                    file.write('[\n\n')
                    for i in range(24):
                        data = { "date": obj.objectList_entsoe[i].date, "hour": obj.objectList_entsoe[i].hour, "entsoe": round(obj.objectList_entsoe[i].price, 2), "tge": round(obj.objectList_tge[i].price, 2) }
                        json_object = json.dumps(data, indent=3)
                        file.write(json_object)
                        if obj.objectList_entsoe[i].hour != 23: file.write(", \n")
                    if index < len(self.dataList)-1:   file.write('\n\n], \n\n')
                    else:   file.write('\n\n] \n\n')
                    index += 1
                    
                file.write(']\n\n')

        except Exception as e:
            print(f"An error occurred in exportToJSON in combinedData: {e}.")
            saveError(str(e) + "  in exportToJSON in combinedData")
            self.errors.errorNumber += 1
            if self.errors.errorNumber <= 10: 
                self.exportToJSON()
            else:   
                self.restartWindow()





    ## zamyka okno 
    def closeWindow(self):
        try:   self.combinedDataButton
        except: print()
        else:   self.combinedDataButton.configure(state='active')

        self.window.destroy()
    




    ## zamyka okno i tworzy nowe
    def restartWindow(self):
        try:
            print('\n\nRestarting combinedData window\n\n')
            self.combinedDataButton.configure(state='active')
            self.window.destroy()
            self.energyPrices_timeInterval = EnergyPrices_timeInterval()
            self.energyPrices_timeInterval.createInterface(self.combinedDataButton)

        except Exception as e:
            print(f"An error occurred in restartWindow in combinedData: {e}.")
            saveError(str(e) + "  in restartWindow in combinedData")










class OneDayObject:
    objectList_entsoe = list()
    objectList_tge = list()

    def copy(self):
        oneDayObject_temp = OneDayObject()
        oneDayObject_temp.objectList_entsoe = self.objectList_entsoe[:]
        oneDayObject_temp.objectList_tge = self.objectList_tge[:]

        return oneDayObject_temp
