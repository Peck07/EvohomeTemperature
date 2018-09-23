from config_helper import *
from Temperature import *
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from datetime import datetime

plugin_name = "InfluxDB"
plugin_type="output"

#influx_logger = logging.getLogger('influx-plugin:')

invalidConfig = False
influx_debug_enabled = True

try:
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read('config.ini')

    influx_write_enabled = not get_boolean_or_default('InfluxDB', 'Simulation', False)

    influx_hostname = config.get("InfluxDB", "hostname")
    influx_port     = config.get("InfluxDB", "port")
    influx_database = config.get("InfluxDB", "database")
    influx_username = config.get("InfluxDB", "username")
    influx_password = config.get("InfluxDB", "password")

    if influx_debug_enabled:
        print("Influx Host: %s:%s Database: %s", influx_hostname, influx_port, influx_database)

except Exception, e:
    print("Error reading config:\n%s", e)
    invalidConfig = True

def prep_record(time, zone, actual, target):
    record_actual = None
    record_target = None
    record_delta = None

    if actual is not None and actual != '':
        try:
            record_actual = {
                "measurement": "zone_temp.actual",
                "tags": {
                    "zone": zone,
                },
                "time": time,
                "fields": {
                    "value": float(actual)
                }
            }
        except Exception as e:
            print e

    if target is not None and target != '':
        try:
            record_target = {
                "measurement": "zone_temp.target",
                "tags": {
                    "zone": zone,
                },
                "time": time,
                "fields": {
                    "value": float(target)
                }
            }
        except Exception as e:
            print e

    if record_actual is not None and record_target is not None:
        record_delta = {
            "measurement": "zone_temp.delta",
            "tags": {
                "zone": zone,
            },
            "time": time,
            "fields": {
                "value": float(actual) - float(target)
            }
        }

    return record_actual, record_target, record_delta


def write(timestamp, temperatures):

    if invalidConfig:
        if influx_debug_enabled:
            print('Invalid config, aborting write')
            return []

    debug_message = 'Writing to ' + plugin_name
    if not influx_write_enabled:
        debug_message += ' [SIMULATED]'
    print(debug_message)

    influx_client = InfluxDBClient(influx_hostname, influx_port, influx_username, influx_password, influx_database)

    debug_row_text = '%s: ' % timestamp
    debug_row_text += '\r\n ' 
    data = []
    for temperature in temperatures:

        record_actual, record_target, record_delta = prep_record(timestamp, temperature.zone,
                                                                 temperature.actual, temperature.target)

        if record_actual:
            data.append(record_actual)
        if record_target:
            data.append(record_target)
        if record_delta:
            data.append(record_delta)

        debug_row_text += "%s (%s A" % (temperature.zone, temperature.actual)
        if temperature.target is not None:
            debug_row_text += ", %s T" % temperature.target
        debug_row_text += ')\r\n '

    if influx_debug_enabled:
        print(debug_row_text)

    try:
        if influx_write_enabled:
            influx_client.write_points(data)
    except InfluxDBClientError as e:
        print str(e)


# if called directly then this is what will execute
if __name__ == "__main__":
    import sys
    temps = []
    temperatures = Temperature(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]) )
    temps.append(temperatures)
    timestamp = datetime.utcnow()
    timestamp = timestamp.replace(microsecond=0) 
    write(timestamp, temps)

