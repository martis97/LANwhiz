"""
AutoConf Network Device Configuration Automation Platform
// Send configuration remotely //

Main Module
"""

from net_auto_config.connect import Connect
from net_auto_config.utils import Utilities
from net_auto_config.config.configure import Configure
from threading import Thread


class AutoConf(object):
    def __init__(self):
        self.connect_to = Connect()

    def configure_cisco_device(
        self,
        hostname,
        mgmt_ip,
        port,
        username,
        password
    ):
        """ Connects to and configures a Cisco device """
        telnet = port == 23 or port >= 5000

        print(f"Starting configuration: {hostname}")

        # Get SSH/Telnet channel
        print(f"{hostname}: Connecting to Cisco Device..")
        connection = self.connect_to.cisco_device(
            mgmt_ip, port, username, password, telnet=telnet
        )
        print(f"{hostname}: Successfully connected")

        self.util = Utilities(connection)
        config = self.util.read_config(hostname)
        print(self.util.get_interfaces())

        # Only configure what's been defined in JSON config file
        methods = [
            method for method in config if not "default_commands" == method
        ]

        config_device = Configure(device_config=config, connection=connection)

        # Ensuring this runs before all
        print("Initialising configuration...")
        config_device.default_commands()
        print("     Done!\n")

        for config_area in methods:
            print("Configuring "
                f"{config_area.replace('_', ' ').title()}..."
            )
            getattr(config_device, config_area)()
            print("    Done!\n")

        print(f"{hostname}: Configuration Complete!")
        print(f"{hostname}: Closing session..")
        connection.cleanup()


cisco_devices = [
{
    "hostname" : "R1",
    "mgmt_ip" : "127.0.0.1",
    "port" : 5000,
    "username" : "admin",
    "password" : "netautoconfig"
},
{
    "hostname" : "R2",
    "mgmt_ip" : "127.0.0.1",
    "port" : 5001,
    "username" : "admin",
    "password" : "netautoconfig"
}]


if __name__ == "__main__":
    ac = AutoConf()
    for device in cisco_devices:
        thread = Thread(target=ac.configure_cisco_device, kwargs=device)
        try:
            thread.start()
        except Exception as e:
            print(f"ERROR: Exception occured on {device['hostname']}")
            print(f"{device['hostname']} says: {e.args}")
            print(f"Terminating configuration for {device['hostname']}")