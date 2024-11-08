from pyModbusTCP.client import ModbusClient





## do testów zmieniania ustawień modbusem
if __name__ == '__main__':
    client = ModbusClient(host='192.168.0.45', port=502, auto_open=True, auto_close=True)
    # client = ModbusClient(host='192.168.0.45', port=502, auto_open=True, auto_close=False)
    
    print(client.write_multiple_registers(121, [1, 2, 2, 20]))
    print(client.read_holding_registers(121, 4))
    client.close()
