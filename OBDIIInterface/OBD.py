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
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping
collections.Mapping = collections.abc.Mapping
collections.Iterable = collections.abc.Iterable
collections.MutableSet = collections.abc.MutableSet
collections.Callable = collections.abc.Callable
import obd
import json
import can

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
    obd.logger.setLevel(obd.logging.DEBUG)


############## ESTABLISH VEHICLE CONNECTION ##############
#Create a connection for use of API Queries
print("Establishing connection...")
#Print all possible ports
if(DEBUG):
    ports = obd.scan_serial()
    print("###\tDEBUG/Available Ports: {0}\t###\n".format(ports))

connection = obd.OBD(fast=False, timeout=30) #Auto connect


'''
bus = can.interface.Bus(channel='can0', bustype='socketcan')
msg= can.Message(arbitration_id=0x7de, data=[0, 25, 0, 1, 3, 1, 4, 1])
bus.send(msg)

notifier = can.Notifier(bus, [can.Printer()])
'''

############## GET INFORMATION FROM VEHICLE ##############
trouble_codes = obd.commands.GET_DTC
#Retrieve DTC Codes
response = connection.query(trouble_codes)


############## SEND REQUESTED INFORMATION ##############
#tc_out = json.dumps(response)
