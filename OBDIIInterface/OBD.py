#!/usr/bin/env python
'''
This program will be hosted on the Raspberry Pi4 and will retrieve the informaiton from the vehicle
Retrieve 
    - Active DTC Codes
    - Current sensor readings
Turn into executable file(?) and then export retrieved data to a .json file or likewise
Parameterize with the requested PID to return requested information

'''
import argparse
#Fix import error for Python 3.10
import sys
import os
import time
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping
collections.Mapping = collections.abc.Mapping
collections.Iterable = collections.abc.Iterable
collections.MutableSet = collections.abc.MutableSet
collections.Callable = collections.abc.Callable
import json
import datetime
import csv
import can
import subprocess
from ctypes import *


################## GLOBALS #####################
global obd2_csv_file
obd2_csv_file = "obd_enabled_pids.csv"

global bitrate
bitrate = 500000

global can_interface
can_interface = "can0"

global base_dir
base_dir = os.path.dirname(os.path.abspath(__file__))

global log_folder
log_folder = '/Log'

global exported_data_file
exported_data_file = "export_data.json"

global exfiltrate_data_time
exfiltrate_data_time = 2



############## PARSE CLI COMMANDS ##############
parser = argparse.ArgumentParser(description= "OBD2 Test Program")
parser.add_argument('-g','--get', help = 'Get the current Diagnostic Troubleshooting Codes (DTCs) from the vehicle', action='store_true')
parser.add_argument('-c','--clear',help = 'Clear the current DTCs from the vehicle',action='store_true')
parser.add_argument('-r','--report',help='Read current sensor values',action='store_true')
parser.add_argument('-d','--debug',help = 'Print debug information to terminal',action='store_true')
args = parser.parse_args()

if args.report == True:
    REPORT = True
else:
    REPORT = False
if args.clear == True:
    CLEAR = True
else: 
    CLEAR = False
if args.get == True:
    GET = True
else:
    GET = False
if args.debug:
    DEBUG = True
else:
    DEBUG = False

if(DEBUG):
    print("###\tDEBUG/ARGUMENTS PASSED: {0}\t###\n".format(args))

if(REPORT and CLEAR):
    exit("Do you know what you're doing?")


##########################################################
############## ESTABLISH VEHICLE CONNECTION ##############
##########################################################
#Create a connection for use of API Queries
print("Establishing connection...")

#Initilize CAN bus
cmd = "chmod u+x can_startup.sh"
modifier = os.system(cmd)
startup = os.system("./can_startup.sh")
print("Starting CAN bus {}\t{}".format(modifier,startup))
bus = can.interface.Bus(channel='can0', bustype='socketcan')


#notifier = can.Notifier(bus, [can.Printer()])

########################################################
############## SEND REQUESTED INFORMATION ##############
########################################################
def _output_message(message):
    """Output the message to the log file\n
    Intended purely as a DEBUG error log for the socket, not OBD/CAN output

    Args:
        message (_type_): Message to place in log file
    """
    print(message)
    try:
        #output_file = os.path.join(log_folder,"log.txt")
        with open("log.txt", "a+") as f:
            f.write(message + "\n")
    except Exception as e:
        if(DEBUG):print("Log fail")
        _output_message("[##LOG##] An exception of type {0} occurred. Arguments:\n{1!r}".format(type(e).__name__,e.args))
        pass

def exfiltrate_data(data):
    """Send the data read from the OBD-II port to a JSON log to be read. This is the main output function

    Args:
        data (_type_): Data to format

    Returns:
        bool: True if the data was logged successfully, False if error occurred
    """
    try:
        #output_file = os.path.join(log_folder,exported_data_file)
        with open('export_data.json', "a+") as f:
            f.write(json.dumps(data)+"\n\n")
        _output_message("Data sent! {0}".format(data))
    except Exception as e:
        if(DEBUG):print("Export fail")
        _output_message("[##EXPORT##] An exception of type {0} occurred. Arguments:\n{1!r}".format(type(e).__name__,e.args))
        return False
    return True

#Assign a timestamp
start = time.time()
#Setup JSON output file
csv_file_path = base_dir + os.sep +obd2_csv_file


##########################################################
############## GET INFORMATION FROM VEHICLE ##############
##########################################################

if(REPORT):
    _output_message("Starting Report:")
    with open(csv_file_path, mode='r') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    service_id = -1
                    pid = -1
                    description = ""
                    formula=""
                    enabled = False
                    if "Enabled" in row:
                        enabled = bool(int(row["Enabled"]))
                    if enabled:
                        if "Mode (hex)" in row:
                            service_id = row["Mode (hex)"]
                            service_int = int(service_id, 16)
                        if "PID (hex)" in row:
                            pid = row["PID (hex)"]
                            pid_int = int(pid, 16)
                        if "Description" in row:
                            description = row["Description"]
                        if "Formula" in row:
                            formula = row["Formula"]

                        if service_int >= 0 and pid_int >= 0:
                            msg = can.Message(arbitration_id=0x7DF, data=[2, service_int, pid_int, 0, 0, 0, 0, 0], is_extended_id=False)
                            if(DEBUG):_output_message("Sending: {}".format(msg))
                            try:
                                bus.send(msg)
                                time.sleep(0.5)
                                for i in range(0, 2):
                                    time.sleep(0.5)
                                    response = bus.recv(timeout=5)
                                    if not response:
                                        message = "No response from CAN bus. Service: {} PID: {} - {}".format(service_id.zfill(2), pid.zfill(2), description)
                                        _output_message(message)
                                        break
                                    if response:
                                        #https://en.wikipedia.org/wiki/OBD-II_PIDs#Standard_PIDs
                                        received_pid = list(response.data)[2]
                                        A = list(response.data)[3]
                                        B = list(response.data)[4]
                                        C = list(response.data)[5]
                                        D = list(response.data)[6]
                                        if service_id == "1":
                                            if len(formula) > 0:
                                                try:
                                                    result = eval(formula)
                                                    message = "{description}: {result}".format(description=description, result=result)
                                                    _output_message(message)
                                                    exfiltrate_data(message)
                                                    if pid_int == int(received_pid):
                                                        if pid_int == int("0C", 16):
                                                            rpm = result
                                                        if pid_int == int("0D", 16):
                                                            speed = result
                                                        if pid_int == int("0F", 16):
                                                            intake_air_temperature = result
                                                except:
                                                    _output_message("Unable to parse formula: {}.".format(formula))
                                        if service_id == "9":
                                            result = ""
                                            try:
                                                for c in list(response.data)[-3:]:
                                                    result += chr(c)
                                                message = "{description}: {result}".format(description=description, result=result)
                                                _output_message(message)
                                                exfiltrate_data(message)
                                            except:
                                                _output_message("Unable to parse response: {}.".format(response.data))
                            except can.CanError:
                                _output_message("CAN error")

                end = time.time()
                hours, rem = divmod(end - start, 3600)
                minutes, seconds = divmod(rem, 60)


if(GET):
    _output_message("Starting GET")
    msg = can.Message(arbitration_id=0x7DF, data=[2, 3, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False, is_rx=False)
    try:
        _output_message("Sending: {}".format(msg))
        bus.send(msg)
        response = bus.recv(timeout=10)
        time.sleep(0.5)
        if not response:
            message = "No response from CAN bus while retrieving DTCs"
            _output_message(message)
        if response:
            _output_message("Response: {}".format(response))
            DTC_class = list(response.data)[2]
            A = list(response.data)[3]
            B = list(response.data)[4]
            C = list(response.data)[5]
            D = list(response.data)[6]
            _output_message("DTC: {} {} {} {} {}".format(DTC_class,A,B,C,D))
            data_log = (DTC_class,A,B,C,D)
            exfiltrate_data(data_log)
    except can.CanError:
        _output_message("CAN Error while getting DTCs")


if(CLEAR):
    _output_message("Starting CLEAR")
    msg = can.Message(arbitration_id=0x7DE, data=[0, 4], is_extended_id=False, is_rx=False)
    for i in range(0,10):
        try:
            _output_message("Attempting to clear DTCs...")
            _output_message("Sending: {}".format(msg))
            bus.send(msg)
            time.sleep(2)
            response = bus.recv(timeout=5)
            if not response:
                message = "No response from CAN bus while clearing DTCs"
                _output_message(message)
            if response:
                #https://en.wikipedia.org/wiki/OBD-II_PIDs#Standard_PIDs
                received_pid = list(response.data)[2]
                A = list(response.data)[3]
                B = list(response.data)[4]
                C = list(response.data)[5]
                D = list(response.data)[6]
                _output_message("Recieved: {} {} {} {} {}\n".format(received_pid,A,B,C,D))
        except can.CanError:
            _output_message("CAN Error while clearing DTCs")
