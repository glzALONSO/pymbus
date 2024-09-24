from pymodbus.client import ModbusSerialClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from openpyxl import Workbook

#Create an empty Dict
decoded_payload = []
responses = {}
#Create client object
client = ModbusSerialClient(port="COM5", baudrate=9600, bytesize=8, parity="E", stopbits=1)
client.connect()
response = client.read_holding_registers(4, 4, slave=34)

print("Read Registers:")
print(response.registers)

# Create the BinaryPayloadDecoder Object
decoder = BinaryPayloadDecoder.fromRegisters(response.registers, 
                                             byteorder=Endian.BIG, 
                                             wordorder=Endian.BIG)



while True:
    try:
        decoded_payload.append(decoder.decode_32bit_uint())
        responses[34] = responses.get(34, decoded_payload) 
    except:
        print("No more values to decode")
        break

print(decoded_payload)
print(responses)
client.close()

if not None:
    print("something happened")




