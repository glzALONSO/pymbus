import logging
import sys
from pymodbus.client import ModbusSerialClient
from pymodbus import ExceptionResponse, FramerType, ModbusException, pymodbus_apply_logging_config

# activate the debugging logger
pymodbus_apply_logging_config("INFO")

def set_up_serial_client(port, framer, baudrate, bytesize, parity, stopbits):
    # Create client Objetc
    client = ModbusSerialClient(port, framer, baudrate, bytesize, parity, stopbits)
    return client

# Connect device, reconnect automatically
def run_sync_serial_client(client, modbuscalls, devices):
    client.connect() 
    if client.connect():
        print("Connection established")
        
        measurements = []
        for modbuscall, device in zip(modbuscalls, devices): 
            if modbuscall:
                print("Running Modbus calls")
                responses = modbuscall(client, device)
                measurements.append(responses)
        client.close()
        return measurements
     
    else:
        print("Connection failed") 
        

# Retrive information from devices
def read_belimo(client, device):
    responses = {}
    try:
        # read_holding_registers(address, count, slave)
        response = client.read_holding_registers(address=7, count=34, slave=device[0])
        print(type(response))
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        raise(exc)

    if response.isError():
        print(f"Received Modbus library error({response})")

    elif isinstance(response, ExceptionResponse):
        print(f"Received Modbus library exception ({response})")
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message

    else:
        responses[device[0]] = responses.get(device[0], response.registers)
    
    print(responses)
    return responses

# Retrive information from devices
def read_zp_meters(client, devices):
    responses = {}
    for device in devices:
        try:
            # read_holding_registers(address, count, slave)
            response = client.read_holding_registers(address=0, count=16, slave=device)

        except ModbusException as exc:
            print(f"Received ModbusException({exc}) from library")
            raise(exc)

        if response.isError():
            print(f"Received Modbus library error({response})")

        elif isinstance(response, ExceptionResponse):
            print(f"Received Modbus library exception ({response})")
            # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message

        else:
            responses[device] = responses.get(device, response.registers)

    print(responses)                
    return responses
            
    
    
def main():
    serial_client = set_up_serial_client(port="COM5", 
                                       framer=FramerType.RTU, 
                                       baudrate=9600, 
                                       bytesize=8, 
                                       parity="E", 
                                       stopbits=1)
    
    measurements = run_sync_serial_client(serial_client, 
                                          [read_belimo, read_zp_meters], 
                                          [[2], [34, 23, 21, 36]])
    

    save_measurements(measurements)    

if __name__ == "__main__":
    main()
