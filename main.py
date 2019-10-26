"""
AutoConf Network Device Configuration Automation Platform
// Send configuration remotely //
b

Main Module
"""

from LANwhiz.connect import Connect
from LANwhiz.utils import Utilities
from LANwhiz.config.configure import ConfigActions
from threading import Thread


class LANwhizMain(object):
    def __init__(self):
        self.connect_to = Connect()

    def configure_cisco_device(self, hostname):
        """ Connects to and configures a Cisco device """

        print(f"Starting configuration: {hostname}")

        device_config = Utilities.read_config(hostname)

        # Determine from port number whether Telnet required
        telnet = device_config["mgmt_port"] == 23 \
                or device_config["mgmt_port"] >= 5000

        # Get SSH/Telnet channel
        print(f"{hostname}: Connecting to Cisco Device..")
        connection = self.connect_to.cisco_device(
            *list(device_config.values())[1:5], telnet=telnet
        )
        print(f"{hostname}: Successfully connected")

        # Only configure what's been defined in JSON config file
        methods = [
            method for method in device_config["config"] 
                if not "default" in method
        ]

        config_device = ConfigActions(
            device_config=device_config["config"], 
            connection=connection
        )

        # Ensuring initial commands are executed first
        print("Initialising configuration...")
        config_device.default_commands()
        print("\tDone!\n")

        for config_area in methods:
            print("Configuring "
                f"{config_area.replace('_', ' ').title()}..."
            )
            getattr(config_device, config_area)()
            print("\tDone!\n")

        print(f"{hostname}: Configuration Complete!")
        print(f"{hostname}: Closing session..")
        connection.cleanup()


if __name__ == "__main__":
    lw = LANwhizMain()
    thread = Thread(target=lw.configure_cisco_device, kwargs={"hostname":"R1"})
    try:
        thread.start()
    except Exception as e:
        # print(f"ERROR: Exception occured on {device['hostname']}")
        # print(f"{device['hostname']} says: {e.args}")
        # print(f"Terminating configuration process for {device['hostname']}")
        pass