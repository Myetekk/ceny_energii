import json
import os



## generuje plik .json z zadanymi danymi
def createJSON(objectList_entsoe, objectList_tge, objectList_entsoe_next, objectList_tge_next): 
    if os.path.exists("outputs") == False: os.mkdir("outputs") 
    with open("outputs\\data.json", "w") as outfile:
        outfile.write('[\n\n')
        for i in range(24):
            data = { "time": objectList_entsoe[i].hour, "entsoe": objectList_entsoe[i].price, "entsoe_next": objectList_entsoe_next[i].price, "tge": objectList_tge[i].price, "tge_next": objectList_tge_next[i].price }
        
            json_object = json.dumps(data, indent=3)

            outfile.write(json_object)
            if objectList_entsoe[i].hour != 23: outfile.write(", \n")
        outfile.write('\n\n]')