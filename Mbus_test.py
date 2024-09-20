from pymodbus.client import ModbusSerialClient

#Create client object
client = ModbusSerialClient(port="COM5", baudrate=9600, bytesize=8, parity="E", stopbits=1)
client.connect()
response = client.read_holding_registers(6, 2, slave=34)
print(response.registers)
client.close()


