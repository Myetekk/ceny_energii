import tkinter as tk
from pyModbusTCP.server import ModbusServer, DataBank
import matplotlib
import matplotlib.pyplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import threading
import time

from webParser_entsoe import parseENTSOE
from webParser_tge import parseTGE
from dataOperations.createJSON import createJSON
from dataOperations.createHTML import createHTML
from dataOperations.createCSV import createCSV
from dataOperations.sendToSQLite import sendToSQLite
from utils import Settings, PlotValues, PlotObj, CheckboxStatus, Errors, checkNumberOfErrors
from settingsOperations import saveSettings_JSON, loadSettings





class EnergyPrices:
    errors = Errors()
    close = False

    window = None

    objectList_entsoe = list()
    objectList_entsoe_next = list()
    objectList_tge = list()
    objectList_tge_next = list()
    objectList_diff = list()
    objectList_diff_next = list() 
    
    dataBank = DataBank()

    date = datetime.datetime.now()
    date_plus_day = datetime.datetime.now() + datetime.timedelta(days=1)





    def main(self):
        print("Loading..")



        self.server = ModbusServer(host='0.0.0.0', port=502, no_block=True, data_bank=self.dataBank)
        self.server.start()

        inteager_thread = threading.Thread(target=self.increaseInteger, daemon = True)
        inteager_thread.start()

        self.errors.errorNumber = 0



        ## ładuje ustawienia z pliku
        self.settings = Settings()
        loadSettings(self.settings, self.errors)


        ## pobiera dane z entsoe i tge dla dnia dzisiejszego i następnego
        parse_entsoe_thread = threading.Thread(target=parseENTSOE, args=(self.date, self.objectList_entsoe, self.errors, self.settings, self.window, ), daemon = True)
        parse_tge_thread = threading.Thread(target=parseTGE, args=(self.date, self.objectList_tge, self.errors, self.settings, self.window, ), daemon = True)
        parse_entsoe_next = threading.Thread(target=parseENTSOE, args=(self.date_plus_day, self.objectList_entsoe_next, self.errors, self.settings, self.window, ), daemon = True)
        parse_tge_next = threading.Thread(target=parseTGE, args=(self.date_plus_day, self.objectList_tge_next, self.errors, self.settings, self.window, ), daemon = True)

        parse_entsoe_thread.start()
        parse_tge_thread.start()
        parse_entsoe_next.start()
        parse_tge_next.start()

        parse_entsoe_thread.join()
        parse_tge_thread.join()
        parse_entsoe_next.join()
        parse_tge_next.join()

        ## ustawienie waluty pobranej z pliku
        if self.objectList_entsoe[0].currency != self.settings.currency:   self.changeCurrency()

        ## ustawienie fixingu pobranego z pliku
        if self.objectList_tge[0].fixing != self.settings.fixing:   self.changeFixing()
        
        self.getDifference()

        self.sendToModbus()

        print("Loaded")

        self.createInterface()


    




    



    ## zmienianie liczby co sekunde (żeby zauważyć kiedy program się zetnie)
    def increaseInteger(self):
        integer = 0
        while True:
            self.dataBank.set_input_registers(address=6, word_list=[integer])
            integer += 1
            if integer == 10: integer=0
            time.sleep(1)










    ## wysyła podane dane przez Modbus
    def sendToModbus(self):
        try: 
            date = datetime.datetime.now()


            objectList= list()
            objectListNext= list()

            if self.settings.data_source == 1:
                objectList = self.objectList_entsoe
                objectListNext = self.objectList_entsoe_next
            else:
                objectList = self.objectList_tge
                objectListNext = self.objectList_tge_next


            blancList = []
            for i in range(120):   blancList += [0] 
            self.dataBank.set_input_registers(address=0, word_list=blancList)


            dateList = [date.year] + [date.month] + [date.day] + [date.hour] + [date.minute] + [date.second]
            self.dataBank.set_input_registers(address=0, word_list=dateList)  ## data i godzina


            euro = str(objectList[0].euro).split('.')
            self.dataBank.set_input_registers(address=7, word_list=[euro[0]])  ## kurs euro, część całkowita 
            self.dataBank.set_input_registers(address=8, word_list=[euro[1]])  ## kurs euro, część dziesiętna 
            

            currentDayList = [] 
            for object in objectList:   
                if object.hour != -1: 
                    currentDayList += [float(object.price)] 
            if len(currentDayList) != 0: 
                self.dataBank.set_input_registers(address=10, word_list=currentDayList)  ## dane z dzisiaj 
                self.dataBank.set_input_registers(address=34, word_list=[1])  ## data_ok
                self.dataBank.set_input_registers(address=35, word_list=[min(currentDayList)])  ## min
                self.dataBank.set_input_registers(address=36, word_list=[max(currentDayList)])  ## max


            nextDayList = []
            for object in objectListNext:   
                if object.hour != -1: 
                    nextDayList += [float(object.price)] 
            if len(nextDayList) != 0: 
                self.dataBank.set_input_registers(address=40, word_list=nextDayList)  ## dane z jutra
                self.dataBank.set_input_registers(address=64, word_list=[1])  ## data_ok
                self.dataBank.set_input_registers(address=65, word_list=[min(nextDayList)])  ## min
                self.dataBank.set_input_registers(address=66, word_list=[max(nextDayList)])  ## max


            currency = 0
            if objectList[0].currency == 'PLN': currency = 1
            elif objectList[0].currency == 'EUR': currency = 2
            self.dataBank.set_input_registers(address=122, word_list=[currency])  ## określa w jakiej walucie są dane (PLN / EUR)
            self.dataBank.set_input_registers(address=123, word_list=[objectList[0].fixing])  ## określa z którego fixingu pochodzą dane (1-fixing1 / 2-fixing2)
            self.dataBank.set_input_registers(address=124, word_list=[objectList[0].data_source])  ## określa z jakiego źródła pochodzą dane (1-entsoe / 2-tge)

        except Exception as e:
            print(f"An error occurred in sendToModbus: {e}. Trying again")
            self.server.stop()
            self.errors.errorNumber += 1
            if self.errors.errorNumber <= 20: 
                self.server.start()
                self.sendToModbus()
            else:   checkNumberOfErrors(self.errors, self.settings, self.window)
    









    ## monitoruje czy ktoś nie próbje zmienić ustawień przez modbusa
    def checkSettingsChange(self):
        try:
            while True:
                settingsListener = self.dataBank.get_holding_registers(122, 3)
                
                currency_number = 1
                if self.settings.currency == 'PLN': currency_number = 1
                elif self.settings.currency == 'EUR': currency_number = 2
                    
                if settingsListener != [0, 0, 0]  and  settingsListener != [currency_number, int(self.settings.fixing), self.settings.data_source]:
                    print("\nupdating settings..")

                    if settingsListener[0] == 1: currency='PLN'
                    elif settingsListener[0] == 2: currency='EUR'
                    if self.settings.currency != currency:
                        self.settings.currency = currency
                        self.currencyStringVar.set(str(self.settings.currency))
                        if self.objectList_tge[0].currency != self.currencyStringVar.get():
                            self.changeCurrency()


                    if self.settings.fixing != settingsListener[1]:
                        self.settings.fixing = settingsListener[1]
                        self.fixingStringVar.set(str(self.settings.fixing))
                        self.changeFixing()
                        
                        if self.objectList_tge[0].currency != self.currencyStringVar.get():
                            self.settings.currency = self.currencyStringVar.get()
                            self.changeCurrency()


                    if self.settings.data_source != settingsListener[2]:
                        self.settings.data_source = settingsListener[2]
                        data_source = 'entsoe'
                        if self.settings.data_source == 1: data_source = 'entsoe'
                        if self.settings.data_source == 2: data_source = 'tge'
                        self.modbusSourceVar.set(data_source)
                        self.sendToModbus()



                    self.reloadElements()
                    self.updateGraph()
                    self.sendToModbus()

                    print("settings updated")
                time.sleep(1)

        except Exception as e:
            print(f"An error occurred in checkSettingsChange: {e}.")
            self.errors.errorNumber += 1
            if self.errors.errorNumber <= 20: 
                self.checkSettingsChange()
            else:   checkNumberOfErrors(self.errors, self.settings, self.window)
            time.sleep(1)










    ## obliczenie różnic entsoe i tge
    def getDifference(self):
        self.objectList_diff.clear()
        self.objectList_diff_next.clear()
        for i in range(len(self.objectList_entsoe)):
            self.objectList_diff.insert(len(self.objectList_diff), round(float(self.objectList_entsoe[i].price) - float(self.objectList_tge[i].price), 2))
            self.objectList_diff_next.insert(len(self.objectList_diff_next), round(float(self.objectList_entsoe_next[i].price) - float(self.objectList_tge_next[i].price), 2))
    









    ## zmienia walute danych
    def changeCurrency(self):
        multiply = 1
        if self.settings.currency == 'EUR':
            multiply = self.objectList_entsoe[0].euro
            for i in range(24):
                self.objectList_entsoe[i].price = float(self.objectList_entsoe[i].price) / multiply
                self.objectList_entsoe_next[i].price = float(self.objectList_entsoe_next[i].price) / multiply
                self.objectList_tge[i].price = float(self.objectList_tge[i].price) / multiply
                self.objectList_tge_next[i].price = float(self.objectList_tge_next[i].price) / multiply

                self.objectList_entsoe[i].currency = 'EUR'
                self.objectList_entsoe_next[i].currency = 'EUR'
                self.objectList_tge[i].currency = 'EUR'
                self.objectList_tge_next[i].currency = 'EUR'
        elif self.settings.currency == 'PLN':
            multiply = 1 / self.objectList_entsoe[0].euro
            for i in range(24):
                self.objectList_entsoe[i].price = float(self.objectList_entsoe[i].price) / multiply
                self.objectList_entsoe_next[i].price = float(self.objectList_entsoe_next[i].price) / multiply
                self.objectList_tge[i].price = float(self.objectList_tge[i].price) / multiply
                self.objectList_tge_next[i].price = float(self.objectList_tge_next[i].price) / multiply
                
                self.objectList_entsoe[i].currency = 'PLN'
                self.objectList_entsoe_next[i].currency = 'PLN'
                self.objectList_tge[i].currency = 'PLN'
                self.objectList_tge_next[i].currency = 'PLN'










    ## zmienia fixing dla tge
    def changeFixing(self):
        if str(self.settings.fixing) == '1':
            for i in range(24):
                self.objectList_tge[i].price = float(self.objectList_tge[i].pricef1)
                self.objectList_tge_next[i].price = float(self.objectList_tge_next[i].pricef1)
                
                self.objectList_tge[i].currency = 'PLN'
                self.objectList_tge_next[i].currency = 'PLN'
                self.objectList_tge[i].fixing = 1
                self.objectList_tge_next[i].fixing = 1
        elif str(self.settings.fixing) == '2': 
            for i in range(24):
                self.objectList_tge[i].price = float(self.objectList_tge[i].pricef2)
                self.objectList_tge_next[i].price = float(self.objectList_tge_next[i].pricef2)
                
                self.objectList_tge[i].currency = 'PLN'
                self.objectList_tge_next[i].currency = 'PLN'
                self.objectList_tge[i].fixing = 2
                self.objectList_tge_next[i].fixing = 2
        
        if self.objectList_tge[0].currency != self.settings.currency:
            multiply = 1
            if self.settings.currency == 'EUR':
                multiply = self.objectList_tge[0].euro
                for i in range(24):
                    self.objectList_tge[i].price = float(self.objectList_tge[i].price) / multiply
                    self.objectList_tge_next[i].price = float(self.objectList_tge_next[i].price) / multiply

                    self.objectList_tge[i].currency = 'EUR'
                    self.objectList_tge_next[i].currency = 'EUR'
            elif self.settings.currency == 'PLN':
                multiply = 1 / self.objectList_tge[0].euro
                for i in range(24):
                    self.objectList_tge[i].price = float(self.objectList_tge[i].price) / multiply
                    self.objectList_tge_next[i].price = float(self.objectList_tge_next[i].price) / multiply
                    
                    self.objectList_tge[i].currency = 'PLN'
                    self.objectList_tge_next[i].currency = 'PLN'
    









    ## przeładowuje wszystkie dane  
    def reloadElements(self):
        self.getDifference()

        ## czyści tabele 
        for gridCell in self.window.grid_slaves():
            if int(gridCell.grid_info()["row"]) >= 2   and   int(gridCell.grid_info()["row"]) <= 25   and   int(gridCell.grid_info()["column"]) in [2,3,5,6,8,9]:
                gridCell.destroy()

        ## wpisuje nowe wartości
        for i in range(24):            
            tk.Label(text=(round(self.objectList_entsoe[i].price, 2))).grid(row=i+2, column=2)
            tk.Label(text=(round(self.objectList_entsoe_next[i].price, 2))).grid(row=i+2, column=3)
            tk.Label(text=(round(self.objectList_tge[i].price, 2))).grid(row=i+2, column=5)
            tk.Label(text=(round(self.objectList_tge_next[i].price, 2))).grid(row=i+2, column=6)
            tk.Label(text=(self.objectList_diff[i])).grid(row=i+2, column=8)
            tk.Label(text=(self.objectList_diff_next[i])).grid(row=i+2, column=9)










    ## uaktualnienie danych na wykresie (po przełączeniu któregoś z checkboxów, lub po pobraniu nowych danych)
    def updateGraph(self):
        hour = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23)
        plotValues = PlotValues()

        plotValues.value_entsoe = (float(self.objectList_entsoe[0].price), float(self.objectList_entsoe[1].price), float(self.objectList_entsoe[2].price), float(self.objectList_entsoe[3].price), float(self.objectList_entsoe[4].price), float(self.objectList_entsoe[5].price), float(self.objectList_entsoe[6].price), float(self.objectList_entsoe[7].price), float(self.objectList_entsoe[8].price), float(self.objectList_entsoe[9].price), float(self.objectList_entsoe[10].price), float(self.objectList_entsoe[11].price), float(self.objectList_entsoe[12].price), float(self.objectList_entsoe[13].price), float(self.objectList_entsoe[14].price), float(self.objectList_entsoe[15].price), float(self.objectList_entsoe[16].price), float(self.objectList_entsoe[17].price), float(self.objectList_entsoe[18].price), float(self.objectList_entsoe[19].price), float(self.objectList_entsoe[20].price), float(self.objectList_entsoe[21].price), float(self.objectList_entsoe[22].price), float(self.objectList_entsoe[23].price))
        plotValues.value_entsoe_next = (float(self.objectList_entsoe_next[0].price), float(self.objectList_entsoe_next[1].price), float(self.objectList_entsoe_next[2].price), float(self.objectList_entsoe_next[3].price), float(self.objectList_entsoe_next[4].price), float(self.objectList_entsoe_next[5].price), float(self.objectList_entsoe_next[6].price), float(self.objectList_entsoe_next[7].price), float(self.objectList_entsoe_next[8].price), float(self.objectList_entsoe_next[9].price), float(self.objectList_entsoe_next[10].price), float(self.objectList_entsoe_next[11].price), float(self.objectList_entsoe_next[12].price), float(self.objectList_entsoe_next[13].price), float(self.objectList_entsoe_next[14].price), float(self.objectList_entsoe_next[15].price), float(self.objectList_entsoe_next[16].price), float(self.objectList_entsoe_next[17].price), float(self.objectList_entsoe_next[18].price), float(self.objectList_entsoe_next[19].price), float(self.objectList_entsoe_next[20].price), float(self.objectList_entsoe_next[21].price), float(self.objectList_entsoe_next[22].price), float(self.objectList_entsoe_next[23].price))
        plotValues.value_tge = (float(self.objectList_tge[0].price), float(self.objectList_tge[1].price), float(self.objectList_tge[2].price), float(self.objectList_tge[3].price), float(self.objectList_tge[4].price), float(self.objectList_tge[5].price), float(self.objectList_tge[6].price), float(self.objectList_tge[7].price), float(self.objectList_tge[8].price), float(self.objectList_tge[9].price), float(self.objectList_tge[10].price), float(self.objectList_tge[11].price), float(self.objectList_tge[12].price), float(self.objectList_tge[13].price), float(self.objectList_tge[14].price), float(self.objectList_tge[15].price), float(self.objectList_tge[16].price), float(self.objectList_tge[17].price), float(self.objectList_tge[18].price), float(self.objectList_tge[19].price), float(self.objectList_tge[20].price), float(self.objectList_tge[21].price), float(self.objectList_tge[22].price), float(self.objectList_tge[23].price))
        plotValues.value_tge_next = (float(self.objectList_tge_next[0].price), float(self.objectList_tge_next[1].price), float(self.objectList_tge_next[2].price), float(self.objectList_tge_next[3].price), float(self.objectList_tge_next[4].price), float(self.objectList_tge_next[5].price), float(self.objectList_tge_next[6].price), float(self.objectList_tge_next[7].price), float(self.objectList_tge_next[8].price), float(self.objectList_tge_next[9].price), float(self.objectList_tge_next[10].price), float(self.objectList_tge_next[11].price), float(self.objectList_tge_next[12].price), float(self.objectList_tge_next[13].price), float(self.objectList_tge_next[14].price), float(self.objectList_tge_next[15].price), float(self.objectList_tge_next[16].price), float(self.objectList_tge_next[17].price), float(self.objectList_tge_next[18].price), float(self.objectList_tge_next[19].price), float(self.objectList_tge_next[20].price), float(self.objectList_tge_next[21].price), float(self.objectList_tge_next[22].price), float(self.objectList_tge_next[23].price))
        plotValues.value_diff = ((float(self.objectList_tge[0].price)+float(self.objectList_diff[0])/2), (float(self.objectList_tge[1].price)+float(self.objectList_diff[1])/2), (float(self.objectList_tge[2].price)+float(self.objectList_diff[2])/2), (float(self.objectList_tge[3].price)+float(self.objectList_diff[3])/2), (float(self.objectList_tge[4].price)+float(self.objectList_diff[4])/2), (float(self.objectList_tge[5].price)+float(self.objectList_diff[5])/2), (float(self.objectList_tge[6].price)+float(self.objectList_diff[6])/2), (float(self.objectList_tge[7].price)+float(self.objectList_diff[7])/2), (float(self.objectList_tge[8].price)+float(self.objectList_diff[8])/2), (float(self.objectList_tge[9].price)+float(self.objectList_diff[9])/2), (float(self.objectList_tge[10].price)+float(self.objectList_diff[10])/2), (float(self.objectList_tge[11].price)+float(self.objectList_diff[11])/2), (float(self.objectList_tge[12].price)+float(self.objectList_diff[12])/2), (float(self.objectList_tge[13].price)+float(self.objectList_diff[13])/2), (float(self.objectList_tge[14].price)+float(self.objectList_diff[14])/2), (float(self.objectList_tge[15].price)+float(self.objectList_diff[15])/2), (float(self.objectList_tge[16].price)+float(self.objectList_diff[16])/2), (float(self.objectList_tge[17].price)+float(self.objectList_diff[17])/2), (float(self.objectList_tge[18].price)+float(self.objectList_diff[18])/2), (float(self.objectList_tge[19].price)+float(self.objectList_diff[19])/2), (float(self.objectList_tge[20].price)+float(self.objectList_diff[20])/2), (float(self.objectList_tge[21].price)+float(self.objectList_diff[21])/2), (float(self.objectList_tge[22].price)+float(self.objectList_diff[22])/2), (float(self.objectList_tge[23].price)+float(self.objectList_diff[23])/2))
        plotValues.value_diff_next = ((float(self.objectList_tge_next[0].price)+float(self.objectList_diff_next[0])/2), (float(self.objectList_tge_next[1].price)+float(self.objectList_diff_next[1])/2), (float(self.objectList_tge_next[2].price)+float(self.objectList_diff_next[2])/2), (float(self.objectList_tge_next[3].price)+float(self.objectList_diff_next[3])/2), (float(self.objectList_tge_next[4].price)+float(self.objectList_diff_next[4])/2), (float(self.objectList_tge_next[5].price)+float(self.objectList_diff_next[5])/2), (float(self.objectList_tge_next[6].price)+float(self.objectList_diff_next[6])/2), (float(self.objectList_tge_next[7].price)+float(self.objectList_diff_next[7])/2), (float(self.objectList_tge_next[8].price)+float(self.objectList_diff_next[8])/2), (float(self.objectList_tge_next[9].price)+float(self.objectList_diff_next[9])/2), (float(self.objectList_tge_next[10].price)+float(self.objectList_diff_next[10])/2), (float(self.objectList_tge_next[11].price)+float(self.objectList_diff_next[11])/2), (float(self.objectList_tge_next[12].price)+float(self.objectList_diff_next[12])/2), (float(self.objectList_tge_next[13].price)+float(self.objectList_diff_next[13])/2), (float(self.objectList_tge_next[14].price)+float(self.objectList_diff_next[14])/2), (float(self.objectList_tge_next[15].price)+float(self.objectList_diff_next[15])/2), (float(self.objectList_tge_next[16].price)+float(self.objectList_diff_next[16])/2), (float(self.objectList_tge_next[17].price)+float(self.objectList_diff_next[17])/2), (float(self.objectList_tge_next[18].price)+float(self.objectList_diff_next[18])/2), (float(self.objectList_tge_next[19].price)+float(self.objectList_diff_next[19])/2), (float(self.objectList_tge_next[20].price)+float(self.objectList_diff_next[20])/2), (float(self.objectList_tge_next[21].price)+float(self.objectList_diff_next[21])/2), (float(self.objectList_tge_next[22].price)+float(self.objectList_diff_next[22])/2), (float(self.objectList_tge_next[23].price)+float(self.objectList_diff_next[23])/2))

        ## stworzenie wykresu, ustawienie podstawowych właściwości
        self.plotObj.plot.clear()
        self.plotObj.plot.set_xlabel("hour")
        self.plotObj.plot.set_ylabel("price")
        self.plotObj.plot.set_title(str(self.objectList_entsoe[0].date) + ",   EUR to PLN: " + str(self.objectList_entsoe[0].euro))
        self.plotObj.plot.grid(which='both')

        ## nałożenie na wykres danych, które są uruchomione domyślnie
        if self.checkboxStatus.entsoe_today_checked: self.plotObj.plot.step(hour, plotValues.value_entsoe, '#b3570c', where='mid', linewidth=0.8)  ## wykres entsoe
        if self.checkboxStatus.entsoe_tomorrow_checked: self.plotObj.plot.step(hour, plotValues.value_entsoe_next, '#ff7d12', where='mid', linewidth=0.8, linestyle='--')  ## wykres entsoe_next
        if self.checkboxStatus.tge_today_checked: self.plotObj.plot.step(hour, plotValues.value_tge, '#00b3b3', where='mid', linewidth=0.8)  ## wykres tge
        if self.checkboxStatus.tge_tomorrow_checked: self.plotObj.plot.step(hour, plotValues.value_tge_next, '#00ffff', where='mid', linewidth=0.8, linestyle='--')  ## wykres tge_next
        if self.checkboxStatus.diff_today_checked: self.plotObj.plot.step(hour, plotValues.value_tge, '#45e600', where='mid', linewidth=0.8)  ## wykres diff
        if self.checkboxStatus.diff_tomorrow_checked: self.plotObj.plot.step(hour, plotValues.value_tge_next, '#2e9900', where='mid', linewidth=0.8, linestyle='--')  ## wykres diff_next
        
        legend_list = []
        entsoe_legend = 'entsoe'
        entsoe_next_legend = 'entsoe_next'
        tge_legend = 'tge'
        tge_next_legend = 'tge_next'
        diff_legend = 'diff'
        diff_next_legend = 'diff_next'
        if self.checkboxStatus.entsoe_today_checked: legend_list.append(entsoe_legend)
        if self.checkboxStatus.entsoe_tomorrow_checked: legend_list.append(entsoe_next_legend)
        if self.checkboxStatus.tge_today_checked: legend_list.append(tge_legend)
        if self.checkboxStatus.tge_tomorrow_checked: legend_list.append(tge_next_legend)
        if self.checkboxStatus.diff_today_checked: legend_list.append(diff_legend)
        if self.checkboxStatus.diff_tomorrow_checked: legend_list.append(diff_next_legend)
        self.plotObj.plot.legend(legend_list) 

            

        ## zmaterializowanie wykresu 
        self.plotObj.canvas.figure = self.plotObj.fig
        self.plotObj.canvas.draw() 
        self.plotObj.canvas.get_tk_widget().grid(row=2, column=11, rowspan=24)










    ## tworzy interfejs
    def createInterface(self):
        ## stworzenie okna
        self.window = tk.Tk()
        self.window.title('Energy prices')
        self.window.resizable(False, False)


    
        ## stworzenie elementów wykresu
        self.plotObj = PlotObj()
        self.plotObj.fig = matplotlib.figure.Figure(figsize=(9, 6.2), dpi=100)
        self.plotObj.canvas = FigureCanvasTkAgg(self.plotObj.fig, master=self.window)
        self.plotObj.plot = self.plotObj.fig.add_subplot(111)


        
        ## sprawdza czy przez Modbusa została przesłana chęć zmiany ustawień
        checkSettingsChange_thread = threading.Thread(target=self.checkSettingsChange, daemon=True)
        checkSettingsChange_thread.start()





        ## ustawia odowiednie wartości gdy wykres jest włączony
        self.checkboxStatus = CheckboxStatus()
        def prepareUpdateGraph():
            self.checkboxStatus.entsoe_today_checked = bool(int(entsoe_today_checkbox.get()))
            self.checkboxStatus.entsoe_tomorrow_checked = bool(int(entsoe_tomorrow_checkbox.get()))
            self.checkboxStatus.tge_today_checked = bool(int(tge_today_checkbox.get()))
            self.checkboxStatus.tge_tomorrow_checked = bool(int(tge_tomorrow_checkbox.get()))
            self.checkboxStatus.diff_today_checked = bool(int(diff_today_checkbox.get()))
            self.checkboxStatus.diff_tomorrow_checked = bool(int(diff_tomorrow_checkbox.get()))
            self.updateGraph()
        

        tk.Label(text="time", font="10").grid(row=0, column=0)
        

        entsoe_today = tk.Frame(self.window)
        tk.Label(entsoe_today, text=("entsoe"), font="10").pack()
        entsoe_today_checkbox = tk.IntVar(entsoe_today)
        entsoe_today_checkbox.set(1)
        tk.Checkbutton(entsoe_today, text=("today"), variable=entsoe_today_checkbox, command=prepareUpdateGraph, onvalue=1, offvalue=0, fg='#999999').pack()
        entsoe_today.grid(row=0, column=2)

        entsoe_tomorrow = tk.Frame(self.window)
        tk.Label(entsoe_tomorrow, text=(" "), fg='#999999').pack()
        entsoe_tomorrow_checkbox = tk.IntVar(entsoe_tomorrow)
        tk.Checkbutton(entsoe_tomorrow, text=("tomorrow"), variable=entsoe_tomorrow_checkbox, command=prepareUpdateGraph, onvalue=1, offvalue=0, fg='#999999').pack()
        entsoe_tomorrow.grid(row=0, column=3)
        

        tge_today = tk.Frame(self.window)
        tk.Label(tge_today, text=("tge"), font="10").pack()
        tge_today_checkbox = tk.IntVar(tge_today)
        tge_today_checkbox.set(1)
        tk.Checkbutton(tge_today, text=("today"), variable=tge_today_checkbox, command=prepareUpdateGraph, onvalue=1, offvalue=0, fg='#999999').pack()
        tge_today.grid(row=0, column=5)

        tge_tomorrow = tk.Frame(self.window)
        tk.Label(tge_tomorrow, text=(" "), fg='#999999').pack()
        tge_tomorrow_checkbox = tk.IntVar(tge_tomorrow)
        tk.Checkbutton(tge_tomorrow, text=("tomorrow"), variable=tge_tomorrow_checkbox, command=prepareUpdateGraph, onvalue=1, offvalue=0, fg='#999999').pack()
        tge_tomorrow.grid(row=0, column=6)
        

        difference_today = tk.Frame(self.window)
        tk.Label(difference_today, text=("defference"), font="10").pack()
        diff_today_checkbox = tk.IntVar(difference_today)
        tk.Checkbutton(difference_today, text=("today"), variable=diff_today_checkbox, command=prepareUpdateGraph, onvalue=1, offvalue=0, fg='#999999').pack()
        difference_today.grid(row=0, column=8)

        difference_tomorrow = tk.Frame(self.window)
        tk.Label(difference_tomorrow, text=("entsoe-tge"), fg='#999999').pack()
        diff_tomorrow_checkbox = tk.IntVar(difference_tomorrow)
        tk.Checkbutton(difference_tomorrow, text=("tomorrow"), variable=diff_tomorrow_checkbox, command=prepareUpdateGraph, onvalue=1, offvalue=0, fg='#999999').pack()
        difference_tomorrow.grid(row=0, column=9)
    




        ## ustawienie przegród tabeli
        tk.Frame(bg='black', width=1, height=70).grid(row=0, column=1)
        tk.Frame(bg='black', width=1, height=70).grid(row=0, column=4)
        tk.Frame(bg='black', width=1, height=70).grid(row=0, column=7)
        tk.Frame(bg='black', width=1, height=70).grid(row=0, column=10)

        tk.Frame(bg='black', width=70, height=1).grid(row=1, column=0)
        tk.Frame(bg='black', width=60, height=1).grid(row=1, column=1)
        tk.Frame(bg='black', width=60, height=1).grid(row=1, column=2)
        tk.Frame(bg='black', width=80, height=1).grid(row=1, column=3)
        tk.Frame(bg='black', width=60, height=1).grid(row=1, column=4)
        tk.Frame(bg='black', width=60, height=1).grid(row=1, column=5)
        tk.Frame(bg='black', width=80, height=1).grid(row=1, column=6)
        tk.Frame(bg='black', width=60, height=1).grid(row=1, column=7)
        tk.Frame(bg='black', width=80, height=1).grid(row=1, column=8)
        tk.Frame(bg='black', width=80, height=1).grid(row=1, column=9)
        tk.Frame(bg='black', width=80, height=1).grid(row=1, column=10)
        tk.Frame(bg='black', width=900, height=1).grid(row=1, column=11)
        
        for i in range(24):
            hour = str(i) + ":00 - " + str(i+1) + ":00"
            tk.Label(text=hour).grid(row=i+2, column=0)

            tk.Label(text=round(float(self.objectList_entsoe[i].price), 2)).grid(row=i+2, column=2)
            tk.Label(text=round(float(self.objectList_entsoe_next[i].price), 2)).grid(row=i+2, column=3)
            tk.Label(text=round(float(self.objectList_tge[i].price), 2)).grid(row=i+2, column=5)
            tk.Label(text=round(float(self.objectList_tge_next[i].price), 2)).grid(row=i+2, column=6)
            tk.Label(text=round(float(self.objectList_diff[i]), 2)).grid(row=i+2, column=8)
            tk.Label(text=round(float(self.objectList_diff_next[i]), 2)).grid(row=i+2, column=9)
            
            tk.Frame(bg='black', width=1, height=27).grid(row=i+2, column=1)
            tk.Frame(bg='black', width=1, height=27).grid(row=i+2, column=4)
            tk.Frame(bg='black', width=1, height=27).grid(row=i+2, column=7)
            tk.Frame(bg='black', width=1, height=27).grid(row=i+2, column=10)

        



        self.managementFrame = tk.Frame(self.window)
        



        ## zapisywaine danych do plików
        def JSON(): createJSON(self.objectList_entsoe, self.objectList_tge, self.objectList_entsoe_next, self.objectList_tge_next, self.errors, self.settings, self.window)
        def HTML(): createHTML(self.objectList_entsoe, self.objectList_tge, self.objectList_entsoe_next, self.objectList_tge_next, self.errors, self.settings, self.window)
        def CSV(): createCSV(self.objectList_entsoe, self.objectList_tge, self.objectList_entsoe_next, self.objectList_tge_next, self.errors, self.settings, self.window)
        def database(): sendToSQLite(self.objectList_entsoe, self.objectList_tge, self.objectList_entsoe_next, self.objectList_tge_next, self.errors, self.settings, self.window)

        JSONbutton = tk.Button(self.managementFrame, text="JSON", command=JSON)
        HTMLbutton = tk.Button(self.managementFrame, text="HTML", command=HTML)
        CSVbutton = tk.Button(self.managementFrame, text="CSV", command=CSV)
        databaseButton = tk.Button(self.managementFrame, text="database", command=database)



        ## wybieranie waluty
        def currencySelected():
            if self.objectList_tge[0].currency != self.currencyStringVar.get():
                self.settings.currency = self.currencyStringVar.get()
                self.changeCurrency()
            
            self.getDifference()
            self.reloadElements()
            self.updateGraph()
            self.sendToModbus()
        self.currencyStringVar = tk.StringVar(self.managementFrame, self.settings.currency)
        currencyFrame = tk.Frame(self.managementFrame)
        tk.Label(currencyFrame, text="waluta:").pack(side='top', padx=5)
        tk.Radiobutton(currencyFrame, text='PLN', variable=self.currencyStringVar, value='PLN', command=currencySelected).pack(side='top', padx=5)
        tk.Radiobutton(currencyFrame, text='EUR', variable=self.currencyStringVar, value='EUR', command=currencySelected).pack(side='bottom', padx=5)



        ## wybieranie fixingu
        def fixingSelected():
            self.settings.fixing = self.fixingStringVar.get()
            self.changeFixing()
            
            if self.objectList_tge[0].currency != self.currencyStringVar.get():
                self.settings.currency = self.currencyStringVar.get()
                self.changeCurrency()

            self.getDifference()
            self.reloadElements()
            self.updateGraph()
            self.sendToModbus()
        self.fixingStringVar = tk.StringVar(self.managementFrame, self.settings.fixing)
        fixingFrame = tk.Frame(self.managementFrame)
        tk.Label(fixingFrame, text="fixing tge:").pack(side='top', padx=5)
        tk.Radiobutton(fixingFrame, text='fixing 1', variable=self.fixingStringVar, value='1', command=fixingSelected).pack(side='top', padx=5)
        tk.Radiobutton(fixingFrame, text='fixing 2', variable=self.fixingStringVar, value='2', command=fixingSelected).pack(side='bottom', padx=5)



        ## wybieranie źródłą danych dla Modbusa - entsoe / tge
        def modbusDataSourceSelected():
            if self.modbusSourceVar.get()=="entsoe":   self.settings.data_source = 1
            elif self.modbusSourceVar.get()=="tge":   self.settings.data_source = 2
            self.sendToModbus()
        modbusSourceVar_defaultvalue = 'entsoe'
        if self.settings.data_source == 1: modbusSourceVar_defaultvalue = 'entsoe'
        elif self.settings.data_source == 2: modbusSourceVar_defaultvalue = 'tge'
        self.modbusSourceVar = tk.StringVar(self.managementFrame, modbusSourceVar_defaultvalue)
        modbusSourceFrame = tk.Frame(self.managementFrame)
        tk.Label(modbusSourceFrame, text="źródło danych:").pack(side='top', padx=5)
        tk.Radiobutton(modbusSourceFrame, text='entsoe', variable=self.modbusSourceVar, value='entsoe', command= modbusDataSourceSelected).pack(side='top', padx=5)
        tk.Radiobutton(modbusSourceFrame, text='tge', variable=self.modbusSourceVar, value='tge', command=modbusDataSourceSelected).pack(side='bottom', padx=(5, 23))










        ## umiejscowienie wszystkich elementów frama
        JSONbutton.pack(side='left', padx=5)
        HTMLbutton.pack(side='left', padx=5)
        CSVbutton.pack(side='left', padx=5)
        databaseButton.pack(side='left', padx=5)
        currencyFrame.pack(side='left', padx=(5, 20))
        fixingFrame.pack(side='left', padx=(5, 20))
        modbusSourceFrame.pack(side='left', padx=(5, 20))

        self.managementFrame.grid(row=0, column=11) 

        self.updateGraph()









        def updateData():
            try:
                # if datetime.datetime.now().hour != self.prev_hour: 
                    print("\nupdating..")
                    self.errors.errorNumber = 0
                    print(datetime.datetime.now())

                    self.date = datetime.datetime.now()
                    self.date_plus_day = datetime.datetime.now() + datetime.timedelta(days=1)


                    parse_entsoe_thread = threading.Thread(target=parseENTSOE, args=(self.date, self.objectList_entsoe, self.errors, self.settings, self.window, ), daemon = True)
                    parse_tge_thread = threading.Thread(target=parseTGE, args=(self.date, self.objectList_tge, self.errors, self.settings, self.window, ), daemon = True)
                    parse_entsoe_next = threading.Thread(target=parseENTSOE, args=(self.date_plus_day, self.objectList_entsoe_next, self.errors, self.settings, self.window, ), daemon = True)
                    parse_tge_next = threading.Thread(target=parseTGE, args=(self.date_plus_day, self.objectList_tge_next, self.errors, self.settings, self.window, ), daemon = True)

                    parse_entsoe_thread.start()
                    parse_tge_thread.start()
                    parse_entsoe_next.start()
                    parse_tge_next.start()

                    parse_entsoe_thread.join()
                    parse_tge_thread.join()
                    parse_entsoe_next.join()
                    parse_tge_next.join()


                    ## ustawienie waluty pobranej z pliku
                    if self.objectList_entsoe[0].currency != self.settings.currency:   self.changeCurrency()

                    ## ustawienie fixingu pobranego z pliku
                    if self.objectList_tge[0].fixing != self.settings.fixing:   self.changeFixing()
                    
                    self.getDifference()

                    
                    self.reloadElements()
                    self.updateGraph()
                    self.sendToModbus()
                    sendToSQLite(self.objectList_entsoe, self.objectList_tge, self.objectList_entsoe_next, self.objectList_tge_next, self.errors, self.settings, self.window)


                    self.prev_hour = datetime.datetime.now().hour
                    
                    print("update finished")
                    
                    if self.errors.errorNumber <= 20:   self.window.after(10000, updateData) ##########################################################################################
                    else:   checkNumberOfErrors(self.errors, self.settings, self.window) ##########################################################################################




                # if self.errors.errorNumber <= 20:   self.window.after(60000, updateData) 
                # else:   checkNumberOfErrors(self.errors, self.settings, self.window)
            
            except Exception as e:
                print(f"An error occurred in updateData: {e}. Trying again")
                self.errors.errorNumber += 1
                if self.errors.errorNumber <= 20:   updateData()
                else:   checkNumberOfErrors(self.errors, self.settings, self.window)
                time.sleep(1)



        self.prev_hour = self.date.hour
        self.window.after(10000, updateData)





        def closeWindow():  
            saveSettings_JSON(self.settings, self.errors)
            self.close = True
            self.window.destroy()

        self.window.protocol("WM_DELETE_WINDOW", closeWindow)
        self.window.mainloop()
        









if __name__ == '__main__':
    while True:
        energyPrices = EnergyPrices()
        energyPrices.main()
        
        if energyPrices.close == True:   break




## testowanie: 
#       wysyłanie modbusem
#       - zmiana ustawień modbusem
#       - gdy dane są nieprawidłowe / niepełne
#       - gdy nie ma internetu
#       działanie ciągłe przez dłuższy czas
#       zmiana dnia
#       update o godzinie 

## wysyłanie modbusem danych z dziś i jutro (jakie wysyła 'dataok'? szczególnie gdy nie ma danych)

## -sprawdzanie errorów w każdej funkcji 
