from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import time
       




if __name__ == '__main__':
    client = ModbusClient(host='192.168.31.63', port=502, auto_open=True, auto_close=False)
    while True:
        for i in range(0, 124, 10):
            list_temp = []
            for j in range(i, i+10):
                if client.read_input_registers(j) != None:   list_temp += [   int(  utils.get_list_2comp( client.read_input_registers(j) )[0]  )   ]
            print(list_temp)
        time.sleep(1)
        print('\n\n\n')