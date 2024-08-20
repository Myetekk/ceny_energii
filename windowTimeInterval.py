import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
import threading
import datetime
import pandas
import time
import csv
import os

from webParser_entsoe import parseENTSOE
from webParser_tge import parseTGE
from utils import Settings, Errors





class EnergyPrices_timeInterval:
    window = None
    frame_table = None
    frame_header = None

    CalendarStart = None
    CalendarStop = None
    dataList = list()





    ## ładuje nagłówek z wybieraniem przedziału czasu
    def loadHeader(self):
        date_start_ = self.date_start
        date_stop_ = self.date_stop


        def calendar_onChange(*args):
            self.dataList.clear()
            self.date_start = self.CalendarStart_variable.get()
            self.date_stop = self.CalendarStop_variable.get()
            
            self.getData()
        

        
        self.CalendarStart_variable = tk.StringVar()
        self.CalendarStop_variable = tk.StringVar()
        
        CalendarStart_frame = tk.Frame(self.frame_header, background='#e6f2ec')
        CalendarStop_frame = tk.Frame(self.frame_header, background='#e6f2ec')

        self.CalendarStart = DateEntry(CalendarStart_frame, textvariable=self.CalendarStart_variable, width=11, year=date_start_.year, month=date_start_.month, day=date_start_.day, background='darkblue', foreground='white', date_pattern='yyyy-MM-dd', state='readonly')
        self.CalendarStop = DateEntry(CalendarStop_frame, textvariable=self.CalendarStop_variable, width=11, year=date_stop_.year, month=date_stop_.month, day=date_stop_.day, background='darkblue', foreground='white', date_pattern='yyyy-MM-dd', state='readonly')

        self.CalendarStart.pack(side=RIGHT, pady=20)
        self.CalendarStop.pack(side=RIGHT, pady=20)

        tk.Label(CalendarStart_frame, text="od  ", background='#e6f2ec').pack(side=LEFT, pady=20)
        tk.Label(CalendarStop_frame, text="do  ", background='#e6f2ec').pack(side=LEFT, pady=20)

        CalendarStart_frame.pack()
        CalendarStop_frame.pack()



        # tk.Button(self.frame_header, text='export', command=self.exportToCSV).pack(pady=20, ipadx=3, ipady=3)
            
        
        ## jakoś zmienić
        self.CalendarStart_variable.trace_add('write', calendar_onChange) #######################################
        self.CalendarStop_variable.trace_add('write', calendar_onChange) #######################################


        self.frame_header.pack(side=LEFT, anchor=N, padx=(0, 15))





    ## ładuje dane z bazy danych, w tym czasie pokazuje loading screan
    def getData(self):
        for widget in self.frame_table.winfo_children(): widget.destroy() 
        
        tk.Label(self.frame_table, text='Loading..').pack()
        self.frame_table.pack()

        ## tworzy listę dat i dla każdej z nich pobiera dane
        self.datelist = pandas.date_range(self.date_start, self.date_stop)
        for date in self.datelist: 
            oneDayObject = OneDayObject()
            parse_entsoe_thread = threading.Thread(target=parseENTSOE, args=(date, oneDayObject.objectList_entsoe, self.errors, self.settings, self.window, ), daemon = True)
            parse_tge_thread = threading.Thread(target=parseTGE, args=(date, oneDayObject.objectList_tge, self.errors, self.settings, self.window, ), daemon = True)

            parse_entsoe_thread.start()
            parse_tge_thread.start()

            parse_entsoe_thread.join()
            parse_tge_thread.join()

            self.dataList.append(oneDayObject.copy())


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

        print('\n\nLoaded')





    ## ładuje dane w formie tabelki
    def loadOneDay(self, index):
        self.frame_table_inner = tk.Frame(self.scrollable_frame, background='#666666')
        
        
        headerBackground = '#cccccc'
        tk.Label(self.frame_table_inner, text=(self.dataList[index].objectList_entsoe[0].date), font='Helvetica 10', background=headerBackground).grid(row=0, column=0, padx=1, pady=1, ipadx=2, ipady=2, sticky=NSEW)
        tk.Label(self.frame_table_inner, text='entsoe', font='Helvetica 10 bold', background=headerBackground).grid(row=0, column=1, padx=1, pady=1, ipadx=2, ipady=2, sticky=NSEW)
        tk.Label(self.frame_table_inner, text='tge', font='Helvetica 10 bold', background=headerBackground).grid(row=0, column=3, padx=1, pady=1, ipadx=2, ipady=2, sticky=NSEW)


        self.backgroundColor = '#d9cece'
        for i in range(24):
            if i%2 == 0:   self.backgroundColor = '#d4d9ce'
            else:   self.backgroundColor = '#d9cece'
            
            tk.Label(self.frame_table_inner, text=str(self.dataList[index].objectList_entsoe[i].hour)[:2], font='Helvetica 11 bold', background=self.backgroundColor).grid(row=i+1, column=0, padx=1, pady=1, ipadx=2, ipady=2, sticky=NSEW)
            tk.Label(self.frame_table_inner, text=self.dataList[index].objectList_entsoe[i].price, font='Helvetica 10', background=self.backgroundColor).grid(row=i+1, column=1, padx=1, pady=1, ipadx=2, ipady=2, sticky=NSEW)
            tk.Label(self.frame_table_inner, text=self.dataList[index].objectList_tge[i].price, font='Helvetica 10', background=self.backgroundColor).grid(row=i+1, column=3, padx=1, pady=1, ipadx=2, ipady=2, sticky=NSEW)


        self.frame_table_inner.pack(side=RIGHT, fill=BOTH, expand=1, padx=10, pady=10)





    ## tworzy cały interfejs
    def createInterface(self, errors, settings):
        self.window = tk.Tk()
        self.window.title('PSE Energy prices')
        self.window.geometry('1200x810')
        self.window.resizable(False, False)
        self.window.configure(padx=10, pady=10)
        self.window.configure(background='#e6f2ec')
        
        self.frame_table = tk.Frame(self.window, background='#e6f2ec')
        self.frame_header = tk.Frame(self.window, background='#e6f2ec')


        self.errors = errors
        self.settings = settings


        self.loadHeader()


        parse_pse_thread = threading.Thread(target=self.getData)
        parse_pse_thread.start()


        self.window.protocol("WM_DELETE_WINDOW")
        self.window.mainloop()










class OneDayObject:
    objectList_entsoe = list()
    objectList_tge = list()

    def copy(self):
        oneDayObject_temp = OneDayObject()
        oneDayObject_temp.objectList_entsoe = self.objectList_entsoe[:]
        oneDayObject_temp.objectList_tge = self.objectList_tge[:]

        return oneDayObject_temp










if __name__ == '__main__':
    energyPrices_timeInterval = EnergyPrices_timeInterval()

    energyPrices_timeInterval.date_start = (datetime.datetime.now() - datetime.timedelta(days=1))
    # energyPrices_timeInterval.date_start = datetime.datetime.now()
    energyPrices_timeInterval.date_stop = datetime.datetime.now()

    errors = Errors()
    settings = Settings()
    energyPrices_timeInterval.createInterface(errors, settings)





## zmiana z 'DateEntry' na 'Calendar'
## error przy zmianie dnia
## export do plików 

## integracja z główną aplikacją 