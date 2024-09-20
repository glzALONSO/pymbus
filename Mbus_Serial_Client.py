import logging
import sys
from pymodbus.client import ModbusSerialClient
from pymodbus import ExceptionResponse, FramerType, ModbusException, pymodbus_apply_logging_config

_logger = logging.getLogger(__file__)
_logger.setLevel("DEBUG")

# Create Client Object
def set_up_serial_client(port, framer, baudrate, bytesize, parity, stopbits):
    _logger.info("### Create client object")
    client = ModbusSerialClient(port, framer, baudrate, bytesize, parity, stopbits)
    return client

# Connect device, reconnect automatically
def run_sync_serial_client(client, modbuscalls):
    _logger.info("### Client starting")
    try:
        client.connect() 
        if client.connect():
            print("Connection established")
            if modbuscalls:
                print("Running Modbus calls")
                modbuscalls(client)
            client.close() 
    except Exception:
        raise(Exception)
        

# Retrive information from devices
def test_call(client):
    _logger.info("### Run a few test calls")
    try:
        # read_holding_registers(address, count, slave)
        response = client.read_holding_registers(address=6, count=2, slave=36)
        print(response.registers)
    except ModbusException as exc:
        _logger.error(f"ERROR: exception in pymodbus {exc}")
        raise(exc)
    if response.isError():
        _logger.error("ERROR: Pymodbus returned an error!")

def get_outlet_temperatures(client):
    try:
        t_out_34 = client.read_holding_registers(address=6, count=2, slave=34)
        t_out_23 = client.read_holding_registers(address=6, count=2, slave=23)
        t_out_21 = client.read_holding_registers(address=6, count=2, slave=21)
        t_out_36 = client.read_holding_registers(address=6, count=2, slave=36)
    except ModbusException as exc:
        _logger.error(f"ERROR: exception in pymodbus {exc}")
        raise(exc)
    if t_out_34.isError() or t_out_23.isError() or t_out_21.isError() or t_out_36.isError():
        _logger.error("ERROR: Pymodbus returned an error!")
    
    print(t_out_34.registers, t_out_23.registers, t_out_21.registers, t_out_36.registers)


def main():
    test_client = set_up_serial_client(port="COM5", 
                                       framer=FramerType.RTU, 
                                       baudrate=9600, 
                                       bytesize=8, 
                                       parity="E", 
                                       stopbits=1)
    
    run_sync_serial_client(test_client, test_call)
    
if __name__ == "__main__":
    main()
