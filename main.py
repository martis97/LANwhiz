"""
AutoConf Network Device Configuration Automation Platform
// Send configuration remotely //

Main Module
"""

from net_auto_config.connect import Connect
from net_auto_config.utils import Utilities
from net_auto_config.config.configure import Configure


class AutoConf(object):
    def __init__(self):
        self.connect_to = Connect()
        self.util = Utilities()

    def configure_cisco_device(
        self,
        hostname,
        mgmt_ip,
        port,
        username,
        password
    ):
        """ Adds and configures a Cisco Device """
        config = self.util.read_config(hostname)
        telnet = port == 23 or port <= 5000
        
        connection = self.connect_to.cisco_device(
            mgmt_ip, port, username, password, telnet=telnet
        )

        config_device = Configure(device_config=config, connection=connection)
        
        print(f"Device under automated configuration: {hostname}")
        print("Executing default configuration...", end="")
        config_device.default_commands()
        print(" Done!")

        print("Configuring interfaces...", end="")
        config_device.interfaces()
        print(" Done!")

        print("Configuring lines...", end="")
        config_device.lines()
        print(" Done!")

        print("Configuration Complete!")

        connection.send_command("end", expect_string="")
        connection.disconnect()

if __name__ == "__main__":
    AutoConf().configure_cisco_device(
        hostname="R1",
        mgmt_ip="127.0.0.1",
        port=5000,
        username="admin",
        password="netautoconfig"
        
    )