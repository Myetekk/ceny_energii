import os

from utils import checkNumberOfErrors



## generuje plik .html z zadanymi danymi i przedstawia w formie tabelki
def createHTML(objectList_entsoe, objectList_tge, objectList_entsoe_next, objectList_tge_next, errors, settings, window): 
    try:
        if os.path.exists("outputs") == False: os.mkdir("outputs") 
        with open("outputs\\data.html", "w") as outfile:
            outfile.write('<div>\n\n')

            outfile.write('    <div style="display: flex; align-items: center; justify-content: center">\n')
            outfile.write('        <h3 style="margin-right: 1vw;">' + objectList_entsoe[0].date + '</h3>\n')
            outfile.write('        <h3>EUR to PLN: ' + str(objectList_tge[0].euro) + '</h3>\n')
            outfile.write('    </div>\n\n')

            outfile.write('    <div style="display: flex; align-items: center; justify-content: center">\n')
            outfile.write('        <table>\n')
            outfile.write('            <thead>\n')
            outfile.write('                <tr>\n')
            outfile.write('                    <th style="text-align: right;">\n')
            outfile.write('                        time\n')
            outfile.write('                    </th>\n')
            outfile.write('                    <th style="text-align: right;">\n')
            outfile.write('                        entsoe\n')
            outfile.write('                    </th>\n')
            outfile.write('                    <th style="text-align: right;">\n')
            outfile.write('                        entsoe_next\n')
            outfile.write('                    </th>\n')
            outfile.write('                    <th style="text-align: right;">\n')
            outfile.write('                        tge\n')
            outfile.write('                    </th>\n')
            outfile.write('                    <th style="text-align: right;">\n')
            outfile.write('                        tge_next\n')
            outfile.write('                    </th>\n')
            outfile.write('                </tr>\n')
            outfile.write('            </thead>\n\n')

            outfile.write('            <tbody>\n')
            for i in range(24):
                outfile.write('                <tr>\n')
                outfile.write('                    <td style="padding: 3px; text-align: right;">\n')
                outfile.write('                        ' + str(objectList_entsoe[i].hour) + '\n')
                outfile.write('                    </td>\n')
                outfile.write('                    <td style="padding: 3px; text-align: right;">\n')
                outfile.write('                        ' + str(objectList_entsoe[i].price) + '\n')
                outfile.write('                    </th>\n')
                outfile.write('                    <td style="padding: 3px; text-align: right;">\n')
                outfile.write('                        ' + str(objectList_entsoe_next[i].price) + '\n')
                outfile.write('                    </th>\n')
                outfile.write('                    <td style="padding: 3px; text-align: right;">\n')
                outfile.write('                        ' + str(objectList_tge[i].price) + '\n')
                outfile.write('                    </th>\n')
                outfile.write('                    <td style="padding: 3px; text-align: right;">\n')
                outfile.write('                        ' + str(objectList_tge_next[i].price) + '\n')
                outfile.write('                    </th>\n')
                outfile.write('                </tr>\n')
            outfile.write('            </tbody>\n')
            outfile.write('        </table>\n\n')
            outfile.write('    </div>')
            
            outfile.write('</div>\n\n')
            
    except Exception as e:
        print(f"An error occurred in createHTML: {e}.")
        errors.errorNumber += 1
        if errors.errorNumber <= 20:   createHTML(objectList_entsoe, objectList_tge, objectList_entsoe_next, objectList_tge_next, errors, settings, window)
        else:   checkNumberOfErrors(errors, settings, window)
