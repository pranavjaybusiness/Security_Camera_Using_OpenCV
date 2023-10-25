import json_parser
import backend
import bluetooth
import time
from threading import Thread

# Constants and global variables
CONFIG_PATH = "config/whitelist.json"
WHITE_LISTED_DEVICES = dict()
CONNECTED_DEVICES = list()


def initialize():
    """Load the whitelisted devices and start the monitoring loop in a separate thread."""
    global WHITE_LISTED_DEVICES
    WHITE_LISTED_DEVICES = json_parser.load_config(CONFIG_PATH)
    thread = Thread(target=monitor_bluetooth_devices)
    thread.start()


def monitor_bluetooth_devices():
    """Continuously monitor nearby bluetooth devices and log if they connect or disconnect."""
    print('Whitelisted Device Keys:', WHITE_LISTED_DEVICES.keys())
    while True:
        print("Scanning for bluetooth devices...")
        nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True,
                                                    flush_cache=True, lookup_class=False)

        # Extract device addresses
        nearby_addresses = [str(addr) for addr, name in nearby_devices]

        # Check for new devices that have connected
        for address in nearby_addresses:
            if address in WHITE_LISTED_DEVICES and address not in CONNECTED_DEVICES:
                message = f"{address} - {WHITE_LISTED_DEVICES[address]} has connected"
                backend.send(["LoggingChannel", "Text", message])
                CONNECTED_DEVICES.append(address)

        # Check for devices that have disconnected
        for address in CONNECTED_DEVICES[:]:  # Using a slice to avoid modifying the list while iterating
            if address not in nearby_addresses:
                message = f"{address} - {WHITE_LISTED_DEVICES[address]} has disconnected"
                backend.send(["LoggingChannel", "Text", message])
                CONNECTED_DEVICES.remove(address)

        time.sleep(20)


# Call initialize to start the monitoring
initialize()
