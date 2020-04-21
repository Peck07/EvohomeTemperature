#!/usr/bin/env python

# Script to monitor and read temperatures from Honeywell EvoHome Web API

# Load required libraries
import json
import datetime
import time
import ConfigParser
from evohomeclient2 import EvohomeClient
import evohomeclient
from influx import *

# Set your login details in the 2 fields below
USERNAME = get_string_or_default('Evohome', 'Username', '')
PASSWORD = get_string_or_default('Evohome', 'Password', '')
DEBUG = get_boolean_or_default('Evohome', 'Debug', False)

# Infinite loop every 5 minutes
while True:

# Get current time and all thermostat readings
    try:
        client = evohomeclient.EvohomeClient(USERNAME, PASSWORD)
        client2 = EvohomeClient(USERNAME, PASSWORD, debug=DEBUG)
        temps = []
        if DEBUG:
            print(client2.locations[0]._gateways[0]._control_systems[0].systemModeStatus)
            print(client2.locations[0]._gateways[0]._control_systems[0].activeFaults)
        for device in client.temperatures():
            temperatures = Temperature(device['name'], float(device['temp']), float(device['setpoint']) )
            if DEBUG:
                print temperatures
            temps.append(temperatures)
        timestamp = datetime.utcnow()
        timestamp = timestamp.replace(microsecond=0)
        write(timestamp, temps)

        print ("Sleep 5mins")
        time.sleep(5 * 60)
    except Exception as e:
        print ("An error occured!")
        print (str(e))
        time.sleep(15 * 60)

