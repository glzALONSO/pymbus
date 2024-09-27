from pymodbus import ExceptionResponse, ModbusException
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


class ModbusSlave:
    # define the instance attributes
    def __init__(self, client, dev_addr, byteorder, wordorder):
        # User defined instance attributes
        self.client = client
        self.dev_addr = dev_addr
        self.byteorder = byteorder
        self.wordorder = wordorder
        # Storage
        self.registers = []
        self.decoder = None
        self.decoded_payload = []
        self.measurements = {}

    def set_up_decoder(self):
        if self.byteorder == "big":
            byte_endian = Endian.BIG

        elif self.byteorder == "little":
            byte_endian = Endian.LITTLE
        
        else:
            print(f"Failed to set up decoder for device with address: {self.dev_addr}")
            self.decoder = None
            return
                
        if self.wordorder == "big":
            word_endian = Endian.BIG

        elif self.wordorder== "little":
            word_endian = Endian.LITTLE

        else:
            print(f"Failed to set up decoder for device with address: {self.dev_addr}")
            self.decoder = None
            return
        
        if self.registers == []:
            print(f"No payload to set up a decoder for device with address: {self.dev_addr}")
            self.decoder = None
        else:
            self.decoder = BinaryPayloadDecoder.fromRegisters(self.registers, byteorder=byte_endian, wordorder=word_endian)
        
        return self.decoder
    

    def poll_device(self, start_addr, regs_count):
        try:
            response = self.client.read_holding_registers(address=start_addr, count=regs_count, slave=self.dev_addr)

        except ModbusException as exc:
            print(f"Received ModbusException({exc}) from library")
            self.registers = []
            raise(exc)
        
        if response.isError():
            print(f"Received Modbus library error({response})")
            self.registers = []

        elif isinstance(response, ExceptionResponse):
            print(f"Received Modbus library exception ({response})")
            self.registers = []
            # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message

        else:
            self.registers = response.registers
            
        return self.registers


    def decode_registers(self, decoding_function):
        if self.decoder == None:
            print(f"No decoder buffer found for device with address: {self.dev_addr}")
            self.decoded_payload = []
            return self.decoded_payload
        else:
            if decoding_function:
                try:
                    self.decoded_payload = decoding_function(self.decoder)
                except:
                    print(f"All register from device with address: {self.dev_addr} decoded.")
            else:
                print("Unvalid decoding function")
                
            return self.decoded_payload
    
    def get_measurements(self, start_addr, regs_count, decoding_function):
        self.measurements = {}
        try:
            self.poll_device(start_addr, regs_count)
            self.set_up_decoder()
            self.decode_registers(decoding_function)
            self.measurements[self.dev_addr] = self.measurements.get(self.dev_addr, self.decoded_payload)

        except Exception:
            print("Failed to get measurements")
            raise Exception
        
        return self.measurements
