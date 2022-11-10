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
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping
collections.Mapping = collections.abc.Mapping
collections.Iterable = collections.abc.Iterable
collections.MutableSet = collections.abc.MutableSet
collections.Callable = collections.abc.Callable
import json
import can
from ctypes import *

############## PARSE CLI COMMANDS ##############
parser = argparse.ArgumentParser(description= "OBD2 Test Program")
parser.add_argument('-g','--get', help = 'Get the current Diagnostic Troubleshooting Codes (DTCs) from the vehicle', action='store_true')
parser.add_argument('-c','--clear',help = 'Clear the current DTCs from the vehicle',action='store_true')
parser.add_argument('-r','--report',help='Read current sensor values',action='store_true')
parser.add_argument('-d','--debug',help = 'Print debug information to terminal',action='store_true')
args = parser.parse_args()

if args.debug:
    DEBUG = True
else:
    DEBUG = False

if(DEBUG):
    print("###\tDEBUG/ARGUMENTS PASSED: {0}\t###\n".format(args))

########################################################################
############## BIND C PROGRAM HEADERS TO PYTHON STRUCTURE ##############
########################################################################

# get a handle to the library
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
#try:
#Open a daemon query for multiple shared instances
socket = obdii.OBDIIOpenSocket(ifname="socketcan",shared = 1)
if(DEBUG):
    print("DEBUG/Socket: ",socket)
#except: 
    #print("Connection Error")

'''
bus = can.interface.Bus(channel='can0', bustype='socketcan')
msg= can.Message(arbitration_id=0x7de, data=[0, 25, 0, 1, 3, 1, 4, 1])
bus.send(msg)

notifier = can.Notifier(bus, [can.Printer()])
'''
##########################################################
############## GET INFORMATION FROM VEHICLE ##############
##########################################################

########################################################
############## SEND REQUESTED INFORMATION ##############
########################################################
