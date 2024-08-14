import csv
import os

from utils import checkNumberOfErrors



## generuje plik .csv z zadanymi danymi
def createCSV(objectList_entsoe, objectList_tge, objectList_entsoe_next, objectList_tge_next, errors, settings, window):
    try:
        if os.path.exists("outputs") == False: os.mkdir("outputs") 
        with open("outputs\\data.csv", "w", newline='') as file:
            writer = csv.writer(file)
            
            writer.writerow(["time", "entsoe", "entsoe_next", "tge", "tge_next"])
            for i in range(24):
                writer.writerow([str(objectList_entsoe[i].hour), objectList_entsoe[i].price, objectList_entsoe_next[i].price, objectList_tge[i].price, objectList_tge_next[i].price] )

    except Exception as e:
        print(f"An error occurred in createCSV: {e}.")
        errors.errorNumber += 1
        if errors.errorNumber <= 20:   createCSV(objectList_entsoe, objectList_tge, objectList_entsoe_next, objectList_tge_next, errors, settings, window)
        else:   checkNumberOfErrors(errors, settings, window)
