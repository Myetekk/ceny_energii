from pyModbusTCP.client import ModbusClient





## do testów zmieniania ustawień modbusem
if __name__ == '__main__':
    client = ModbusClient(host='192.168.96.30', port=502, auto_open=True, auto_close=False)
    
    print(client.write_multiple_registers(122, [1, 2, 2]))
    print(client.read_holding_registers(122, 3))
