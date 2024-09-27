from pymodbus.client import ModbusSerialClient
from pymodbus import FramerType, pymodbus_apply_logging_config
from ModbusSlave import ModbusSlave
from inputimeout import inputimeout
import time

# activate the debugging logger only when an error occurs
pymodbus_apply_logging_config("INFO")

# Create the serial client
def set_up_serial_client(port, framer, baudrate, bytesize, parity, stopbits):
    # Create an istance of the Modbus Serial Client
    client = ModbusSerialClient(port, framer, baudrate, bytesize, parity, stopbits)
    return client


# Connect device, reconnect automatically
def run_sync_serial_client(client, modbus_calls, modbus_frames, devices):
    client.connect() 
    if client.connect():
        print("Connection ESTABLISHED")
        
        measurements = []
        for modbus_call, modbus_frame, device in zip(modbus_calls, modbus_frames, devices): 
            if modbus_call:
                print("Running Modbus calls...")
                # responses is a list of dictionaries
                responses = modbus_call(client, device, modbus_frame)
                measurements.append(responses)
        client.close()
        return measurements
     
    else:
        print("Connection FAILED")


# Create the decoding functions to decode the payloads
def belimo_flow_frames(decoder):
    decoded_payload = []
    decoded_payload.append(decoder.decode_16bit_uint())
    decoded_payload.append(decoder.decode_16bit_uint())
    decoded_payload.append(decoder.decode_16bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    return decoded_payload


def belimo_temp_frames(decoder):
    decoded_payload = []
    decoded_payload.append(decoder.decode_16bit_int())
    decoded_payload.append(decoder.decode_16bit_int())
    decoded_payload.append(decoder.decode_16bit_int())
    decoded_payload.append(decoder.decode_16bit_int())
    decoded_payload.append(decoder.decode_16bit_uint())
    decoded_payload.append(decoder.decode_16bit_uint())
    return decoded_payload


def belimo_pw_frames(decoder):
    decoded_payload = []
    decoded_payload.append(decoder.decode_16bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    return decoded_payload


def belimo_vol_frames(decoder):
    decoded_payload = []
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    return decoded_payload


def belimo_energy_frames(decoder):
    decoded_payload = []
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    return decoded_payload


def zp_meter_frames(decoder):
    decoded_payload = []
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    decoded_payload.append(decoder.decode_32bit_uint())
    return decoded_payload


# Create the csv files
def create_csv_file(file_name, address, header):
    print("Creating CSV files...")

    # create the csv file
    try:
        with open(f"{address}_{file_name}.csv", "w") as csv_file:
            # Create the csv header string
            separator = ", "
            line = separator.join(header)
            # Write the string into the csv file
            csv_file.write(f"{line}\n")
            print(f"CSV file with name: {csv_file.name} created in current directory")
            return csv_file.name
    except:
        print("Could not create csv file")


# Write the measurements in the csv files
# file is a string
# measurements is a list of ints
def write_to_csv(file, measurements):
    try:
        print(f"Opening {file}...")
        # Open the file in append mode
        with open(f"{file}", "a") as csv_file:
            # List of ints ---> list of strings
            meas_str = map(str, measurements)
            separator = ", "
            line = separator.join(meas_str)
            #print(line)
            csv_file.write(f"{line}\n")
        print("Measurements written")
    except:
        print(f"Cannot open {file}...")
        raise(Exception)


# Create csv files based on the device_parameters dict    
def create_all_csv_files(device_parameters, file_names, headers):
    # Create the csv files
    res_files_names = []
    # parameters.values is a iterator with structure: values({}, {})
    # file_names is a list with structure: [[],[]]
    # headers is a list with structure: [[[]],[[]]]
    # resulting iterator structure: (parameters={}, file_names_list=[], headers_list=[[]])
    for parameters, file_names_list, headers_list in zip(device_parameters.values(), file_names, headers):
        # iterate over the addresses(list) in the key "dev_addresses" 
        for address in parameters["dev_addresses"]:
            # file_names_list is a list with structure: [] 
            # headers_list is a list with structure: [[]]
            # resulting iterator ("file_name", [])
            for file_name, header in zip(file_names_list, headers_list):
                res_file = create_csv_file(file_name, address, header)
                res_files_names.append(res_file)

    return res_files_names
                

# get measurements from all modbus slaves
def get_all_measurements(device_parameters, serial_client):
        # Get the measurements from each modbus slave
        measurements_list = []
        # parameters contains the values (dicts) of each key in device_parameters
        for parameters in device_parameters.values():
            # iterate over the addresses(list) in the key "dev_addresses" to instantiate a mbus device with each address in the addresses (list)
            # access the list in the key "endian" to retrive the endian values corresponding to each type of device"
            for address in parameters["dev_addresses"]:
                mbus_device = ModbusSlave(serial_client, address, byteorder=parameters["endian"][0], wordorder=parameters["endian"][1])
                # access the values in the keys "target_registers" (dict) and "decoding_functions" (list)
                # since the value of "target_registers" is a dict access its values as an iterator with structure values([[], []])
                # iterate over the values of the dict in the key "target_registers" ([[], []]) and the values in the key "decoding_functions" ([])
                # resulting iterator ([target_registers], decoding_function)
                for target_registers, decoding_function in zip(parameters["target_registers"].values(), parameters["decoding_functions"]):
                    # access the first element in the list target_registers to get the reading start_address
                    # access the second element in list target_registers to get the number of registers that will be read
                    # pass the decoding function associated with [target_registers]
                    measurements = mbus_device.get_measurements(start_addr=target_registers[0], 
                                                regs_count=target_registers[1], 
                                                decoding_function=decoding_function)
                    
                    measurements_list.append(measurements)
                    
        return measurements_list

# write the measurements retrieved on its corresponding file
def write_all_measurements_to_csv(res_files_names, measurements_list):
    # file is a string, measurements is a list of ints
    # res_file_names is a list with structure [] ---> size = 9
    # measurements list is a list with structure [{}] ---> size = 9
    # iterator structure ("file_name", {})
    for file_name, measurement in zip(res_files_names, measurements_list):
        print(file_name, measurement)
        # measurement.values is an iterator with structure values([[]])
        # for loop will execute once and meas is a list of ints with structure []
        for meas in measurement.values():
            write_to_csv(file_name, meas)


if __name__ == "__main__":
# ------------------------------- INITIAL SETUP --------------------------------------------------------
    # Register the time at which the script started
    start_time = time.time()
    
    # Configure the Python Serial Client
    serial_client = set_up_serial_client(port="COM5", 
                                       framer=FramerType.RTU, 
                                       baudrate=9600, 
                                       bytesize=8, 
                                       parity="E", 
                                       stopbits=1)
    
    
    # Define the file name and the header
    # WARNING: Change the name of each file every time you run the script to avoid overwriting the measurements.
    file_names = [["Belimo_flow", "Belimo_temperature", "Belimo_power" ,"Belimo_vol", "Belimo_energy"], ["ZP_meter_all"]]
    headers = [[["Rel_vol_flow[%]", # 16 bit uint
               "Abs_vol_flow[l/s]", # 16 bit uint 
               "Abs_vol_flow[gpm]", # 16 bit uint 
               "Abs_vol_flow[]"], # 32 bit uint 
               ["T_out[°C]", # 16 bit int ############
               "T_out[°F]", # 16 bit int ############
               "T_in[°C]", # 16 bit int ############
               "T_in[°F]", # 16 bit int ############
               "T_diff[K]", # 16 bit uint
               "T_diff[°F]"], # 16 bit uint
               ["Rel_Pw[%]", # 16 bit uint
               "Abs_C_Pw[kW]", # 32 bit uint 
               "Abs_C_Pw[kBTU/h]", # 32 bit uint 
               "Abs_C_Pw[]", # 32 bit uint
               "Abs_H_Pw[kW]", # 32 bit uint 
               "Abs_H_Pw[kBTU/h]", # 32 bit uint 
               "Abs_H_Pw[]"], # 32 bit uint 
               ["Accum_vol[m^3]", # 32 bit uint 
               "Accum_vol[gpm]", # 32 bit uint 
               "Accum_vol[]"], # 32 bit uint 
               ["Energy_C[kWh]", # 32 bit uint
               "Energy_C[kBTU]", # 32 bit uint
               "Energy_C[]", # 32 bit uint
               "Energy_H[KWh]", # 32 bit uint
               "Energy_H[kBTU]", # 32 bit uint
               "Energy_H[]"]], # 32 bit uint
              [["Energy Accum [KWh]", 
               "None", 
               "T_in[°C]", 
               "T_out[°C]", 
               "T_diff[°C]", 
               "Flow Accum[m^3]", 
               "Flow_Inst[m^3/h]", 
               "Power[kW]"]]] # [[cols_names_belimo], [cols_names_zp_meter]]
    
    
    device_parameters = {"Belimo_EV": {"dev_addresses": [2],
                                       "endian": ["big", "little"],
                                       "target_registers": {"flow": [6, 5],
                                                            "temp": [19, 6],
                                                            "power": [26, 13],
                                                            "volume": [59, 6],
                                                            "Energy": [65, 12]},
                                        "decoding_functions": [belimo_flow_frames, 
                                                               belimo_temp_frames, 
                                                               belimo_pw_frames, 
                                                               belimo_vol_frames, 
                                                                  belimo_energy_frames]},
                         "ZP_meter": {"dev_addresses": [34, 23, 21, 36],
                                      "endian": ["big", "big"],
                                      "target_registers": {"all": [0, 16],},
                                      "decoding_functions": [zp_meter_frames]}}
    

    # Create csv_files based on the device_parameters, file_names and headers
    res_files_names = create_all_csv_files(device_parameters, file_names, headers)
    
# ------------------------------------ INDEFENITE REPETITION --------------------------------------------------------------------------
    # first time do not wait
    # get the measurements from all modbus slaves
    measurements_list = get_all_measurements(device_parameters, serial_client)
    print(measurements_list)
    # write the measurements in its corresponding file
    write_all_measurements_to_csv(res_files_names, measurements_list)
    # report the elapsed time since the script started
    end_time = time.time()
    print("Time since script started:", start_time - end_time)
    

    while True:
        try:
            user_input = inputimeout(prompt="stop?['yes'/'no']", timeout=60)
            if user_input == 'yes':
                break
        except Exception:
            try:
                # get measurements from all modbus slaves
                measurements_list = get_all_measurements(device_parameters, serial_client)
                print(measurements_list)
                # write the measurements in its corresponding file
                write_all_measurements_to_csv(res_files_names, measurements_list)
                # report the elapsed time since the script started
                end_time = time.time()
                print("Time since script started:", start_time - end_time)
            except Exception as exc:
                print("Something went wrong!!!")
                # report the elapsed time since the script started
                end_time = time.time()
                print("Time since script started:", start_time - end_time)
                raise(exc)
            finally:
                continue