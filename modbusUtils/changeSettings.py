from pyModbusTCP.client import ModbusClient





## do testów zmieniania ustawień modbusem
if __name__ == '__main__':
    client = ModbusClient(host='192.168.1.2', port=502, auto_open=True, auto_close=True)
    
    print(client.write_multiple_registers(121, [1, 2, 2, 600]))
    print(client.read_holding_registers(121, 4))
    client.close()
