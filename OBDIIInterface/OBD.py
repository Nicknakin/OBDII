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
log_folder = base_dir + os.sep + "Log"

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

########################################################################
############## BIND C PROGRAM HEADERS TO PYTHON STRUCTURE ##############
########################################################################

# get a handle to the library
#Windows Machine
if sys.platform.__contains__("win"):
    path = ".\obdii-py\\build\libobdii.so"
else: #Linux
    path = "./obdii-py/build/libobdii.so"

try:
    obdii = CDLL(path)
except:
    exit("obdii library not found.\nCheck for directory\t{0}".format(path))

class OBDIISocket(Structure):
    _fields_ = [
            ('s', c_int),
            ('shared', c_short),
            ('ifindex', c_uint),
            ('tid', c_uint32),
            ('rid', c_uint32)
    ]

class OBDIICommand(Structure):
    pass

class OBDIITroubleCodes(Structure):
    _fields_ = [
            ('troubleCodes', POINTER(c_char * 6)),
            ('numTroubleCodes', c_int)
    ]

class OBDIIOxygenSensorVoltageOrCurrent(Union):
    _fields_ = [
            ('voltage', c_float),
            ('current', c_float)
    ]

class OBDIIOxygenSensorTrimOrRatio(Union):
    _fields_ = [
            ('shortTermFuelTrim', c_float),
            ('fuelAirEquivalenceRatio', c_float)
    ]

class OBDIIOxygenSensorValues(Structure):
    _anonymous_ = [ 'voltageOrCurrent', 'trimOrRatio' ]
    _fields_ = [
            ('voltageOrCurrent', OBDIIOxygenSensorVoltageOrCurrent),
            ('trimOrRatio', OBDIIOxygenSensorTrimOrRatio)
    ]

class OBDIIResponseValue(Union):
    _fields_ = [
            ('numericValue', c_float),
            ('bitfieldValue', c_uint32),
            ('stringValue', c_char_p),
            ('DTCs', OBDIITroubleCodes),
            ('oxygenSensorValues', OBDIIOxygenSensorValues)
    ]

class OBDIIResponse(Structure):
    _anonymous_ = [ 'value' ]
    _fields_ = [
            ('success', c_int),
            ('command', POINTER(OBDIICommand)),
            ('value', OBDIIResponseValue)
    ]

# OBDIIResponseType enum
(OBDIIResponseTypeBitfield, OBDIIResponseTypeNumeric, OBDIIResponseTypeString, OBDIIResponseTypeOther) = (0, 1, 2, 3)

OBDIIResponseDecoder = CFUNCTYPE(None, POINTER(OBDIIResponse), POINTER(c_uint8), c_int)

OBDIICommand._fields_ = [
        ('name', c_char_p),
        ('payload', c_uint8 * 2),
        ('responseType', c_int),
        ('expectedResponseLength', c_short),
        ('responseDecoder', OBDIIResponseDecoder)
]

class OBDIIMode1SupportedPIDs(Structure):
    _fields_ = [
            ('_1_to_20', c_uint32),
            ('_21_to_40', c_uint32),
            ('_41_to_60', c_uint32),
            ('_61_to_80', c_uint32)
    ]

class OBDIICommandSet(Structure):
    _fields_ = [
            ('_mode1SupportedPIDs', OBDIIMode1SupportedPIDs),
            ('_mode9SupportedPIDs', c_uint32),
            ('numCommands', c_int),
            ('commands', POINTER(POINTER(OBDIICommand)))
    ]

class OBDIICommandsT(Structure):
    _fields_ = [
        ('mode1SupportedPIDs_1_to_20', POINTER(OBDIICommand)),
        ('monitorStatus', POINTER(OBDIICommand)),
        ('freezeDTC', POINTER(OBDIICommand)),
        ('fuelSystemStatus', POINTER(OBDIICommand)),
        ('calculatedEngineLoad', POINTER(OBDIICommand)),
        ('engineCoolantTemperature', POINTER(OBDIICommand)),
        ('bank1ShortTermFuelTrim', POINTER(OBDIICommand)),
        ('bank1LongTermFueldTrim', POINTER(OBDIICommand)),
        ('bank2ShortTermFuelTrim', POINTER(OBDIICommand)),
        ('bank2LongTermFuelTrim', POINTER(OBDIICommand)),
        ('fuelPressure', POINTER(OBDIICommand)),
        ('intakeManifoldAbsolutePressure', POINTER(OBDIICommand)),
        ('engineRPMs', POINTER(OBDIICommand)),
        ('vehicleSpeed', POINTER(OBDIICommand)),
        ('timingAdvance', POINTER(OBDIICommand)),
        ('intakeAirTemperature', POINTER(OBDIICommand)),
        ('mafAirFlowRate', POINTER(OBDIICommand)),
        ('throttlePosition', POINTER(OBDIICommand)),
        ('commandedSecondaryAirStatus', POINTER(OBDIICommand)),
        ('oxygenSensorsPresentIn2Banks', POINTER(OBDIICommand)),
        ('oxygenSensor1_fuelTrim', POINTER(OBDIICommand)),
        ('oxygenSensor2_fuelTrim', POINTER(OBDIICommand)),
        ('oxygenSensor3_fuelTrim', POINTER(OBDIICommand)),
        ('oxygenSensor4_fuelTrim', POINTER(OBDIICommand)),
        ('oxygenSensor5_fuelTrim', POINTER(OBDIICommand)),
        ('oxygenSensor6_fuelTrim', POINTER(OBDIICommand)),
        ('oxygenSensor7_fuelTrim', POINTER(OBDIICommand)),
        ('oxygenSensor8_fuelTrim', POINTER(OBDIICommand)),
        ('conformingStandards', POINTER(OBDIICommand)),
        ('oxygenSensorsPresentIn4Banks', POINTER(OBDIICommand)),
        ('auxiliaryInputStatus', POINTER(OBDIICommand)),
        ('runtimeSinceEngineStart', POINTER(OBDIICommand)),
        ('mode1SupportedPIDs_21_to_40', POINTER(OBDIICommand)),
        ('distanceTraveledWithMalfunctionIndicatorLampOn', POINTER(OBDIICommand)),
        ('fuelRailPressure', POINTER(OBDIICommand)),
        ('fuelRailGaugePressure', POINTER(OBDIICommand)),
        ('oxygenSensor1_fuelAirRatioVoltage', POINTER(OBDIICommand)),
        ('oxygenSensor2_fuelAirRatioVoltage', POINTER(OBDIICommand)),
        ('oxygenSensor3_fuelAirRatioVoltage', POINTER(OBDIICommand)),
        ('oxygenSensor4_fuelAirRatioVoltage', POINTER(OBDIICommand)),
        ('oxygenSensor5_fuelAirRatioVoltage', POINTER(OBDIICommand)),
        ('oxygenSensor6_fuelAirRatioVoltage', POINTER(OBDIICommand)),
        ('oxygenSensor7_fuelAirRatioVoltage', POINTER(OBDIICommand)),
        ('oxygenSensor8_fuelAirRatioVoltage', POINTER(OBDIICommand)),
        ('commandedEGR', POINTER(OBDIICommand)),
        ('egrError', POINTER(OBDIICommand)),
        ('commandedEvaporativePurge', POINTER(OBDIICommand)),
        ('fuelTankLevelInput', POINTER(OBDIICommand)),
        ('warmUpsSinceCodesCleared', POINTER(OBDIICommand)),
        ('distanceTraveledSinceCodesCleared', POINTER(OBDIICommand)),
        ('evaporativeSystemVaporPressure', POINTER(OBDIICommand)),
        ('absoluteBarometricPressure', POINTER(OBDIICommand)),
        ('oxygenSensor1_fuelAirRatioCurrent', POINTER(OBDIICommand)),
        ('oxygenSensor2_fuelAirRatioCurrent', POINTER(OBDIICommand)),
        ('oxygenSensor3_fuelAirRatioCurrent', POINTER(OBDIICommand)),
        ('oxygenSensor4_fuelAirRatioCurrent', POINTER(OBDIICommand)),
        ('oxygenSensor5_fuelAirRatioCurrent', POINTER(OBDIICommand)),
        ('oxygenSensor6_fuelAirRatioCurrent', POINTER(OBDIICommand)),
        ('oxygenSensor7_fuelAirRatioCurrent', POINTER(OBDIICommand)),
        ('oxygenSensor8_fuelAirRatioCurrent', POINTER(OBDIICommand)),
        ('catalystTemperatureBank1Sensor1', POINTER(OBDIICommand)),
        ('catalystTemperatureBank2Sensor1', POINTER(OBDIICommand)),
        ('catalystTemperatureBank1Sensor2', POINTER(OBDIICommand)),
        ('catalystTemperatureBank2Sensor2', POINTER(OBDIICommand)),
        ('mode1SupportedPIDs_41_to_60', POINTER(OBDIICommand)),
        ('currentDriveCycleMonitorStatus', POINTER(OBDIICommand)),
        ('controlModuleVoltage', POINTER(OBDIICommand)),
        ('absoluteLoadValue', POINTER(OBDIICommand)),
        ('fuelAirCommandEquivalenceRatio', POINTER(OBDIICommand)),
        ('relativeThrottlePosition', POINTER(OBDIICommand)),
        ('ambientAirTemperature', POINTER(OBDIICommand)),
        ('absoluteThrottlePositionB', POINTER(OBDIICommand)),
        ('absoluteThrottlePositionC', POINTER(OBDIICommand)),
        ('acceleratorPedalPositionD', POINTER(OBDIICommand)),
        ('acceleratorPedalPositionE', POINTER(OBDIICommand)),
        ('acceleratorPedalPositionF', POINTER(OBDIICommand)),
        ('commandedThrottleActuator', POINTER(OBDIICommand)),
        ('timeRunWithMalfunctionIndicatorLampOn', POINTER(OBDIICommand)),
        ('timeSinceTroubleCodesCleared', POINTER(OBDIICommand)),
        ('DTCs', POINTER(OBDIICommand)),
        ('mode9SupportedPIDs', POINTER(OBDIICommand)),
        ('vinMessageCount', POINTER(OBDIICommand)),
        ('VIN', POINTER(OBDIICommand)),
        ('ECUName', POINTER(OBDIICommand))
    ]

OBDIICommands = OBDIICommandsT.in_dll(obdii, 'OBDIICommands')
OBDIIMode1Commands = (OBDIICommand * 79).in_dll(obdii, 'OBDIIMode1Commands')
OBDIIMode9Commands = (OBDIICommand * 3).in_dll(obdii, 'OBDIIMode9Commands')

OBDIIDecodeResponseForCommand = obdii.OBDIIDecodeResponseForCommand
OBDIIDecodeResponseForCommand.argtypes = [ POINTER(OBDIICommand), POINTER(c_uint8), c_int ]
OBDIIDecodeResponseForCommand.restype = OBDIIResponse

OBDIIResponseFree = obdii.OBDIIResponseFree
OBDIIResponseFree.restype = None
OBDIIResponseFree.argtypes = [ POINTER(OBDIIResponse) ]

OBDIICommandSetContainsCommand = obdii.OBDIICommandSetContainsCommand
OBDIICommandSetContainsCommand.argtypes = [ POINTER(OBDIICommandSet), POINTER(OBDIICommand) ]

OBDIICommandSetFree = obdii.OBDIICommandSetFree
OBDIICommandSetFree.restype = None
OBDIICommandSetFree.argtypes = [ POINTER(OBDIICommandSet) ]

OBDIIOpenSocket = obdii.OBDIIOpenSocket
OBDIIOpenSocket.argtypes = [ POINTER(OBDIISocket), c_char_p, c_uint32, c_uint32, c_int ]

OBDIICloseSocket = obdii.OBDIICloseSocket
OBDIICloseSocket.argtypes = [ POINTER(OBDIISocket) ]

OBDIIPerformQuery = obdii.OBDIIPerformQuery
OBDIIPerformQuery.restype = OBDIIResponse
OBDIIPerformQuery.argtypes = [ POINTER(OBDIISocket), POINTER(OBDIICommand) ]

OBDIIGetSupportedCommands = obdii.OBDIIGetSupportedCommands
OBDIIGetSupportedCommands.restype = OBDIICommandSet
OBDIIGetSupportedCommands.argtypes = [ POINTER(OBDIISocket) ]

# constants from linux/can.h

CAN_EFF_FLAG = 0x80000000

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
##########################################################
############## GET INFORMATION FROM VEHICLE ##############
##########################################################

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
        output_file = "/Log/log.txt"
        with open(output_file, "a") as f:
            f.write(message + "\n")
    except:
        print("Log fail")
        pass

def exfiltrate_data(data):
    """Send the data read from the OBD-II port to a JSON log to be read. This is the main output function

    Args:
        data (_type_): Data to format

    Returns:
        bool: True if the data was logged successfully, False if error occurred
    """
    _output_message("Sending Data...")
    for i in range(0,len(data)):
        dictionary = {i:data[i]}
    try:
        with open("/Log/"+ exported_data_file, "a+") as f:
            f.write(json.dumps(dictionary)+"\n\n")
        _output_message("Data sent!")
    except:
        _output_message("Data not sent!")
        return False
    return True

#Assign a timestamp
start = time.time()
#Setup JSON output file
csv_file_path = base_dir + os.sep +obd2_csv_file

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
                            _output_message("Sending: {}".format(msg))
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
    msg = can.Message(arbitration_id=0x7DF, data=[2, 3, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
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
    except:
        _output_message("CAN Error while getting DTCs")


if(CLEAR):
    _output_message("Starting CLEAR")
    msg = can.Message(arbitration_id=0x7DE, data=[0, 4], is_extended_id=False)
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
                received_pid = list(response.data)[2]
                A = list(response.data)[3]
                B = list(response.data)[4]
                C = list(response.data)[5]
                D = list(response.data)[6]
                _output_message("Recieved: {} {} {} {} {}\n".format(received_pid,A,B,C,D))
        except:
            _output_message("CAN Error while clearing DTCs")
