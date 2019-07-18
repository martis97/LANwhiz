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
        """ Connects to and configures a Cisco device """
        config = self.util.read_config(hostname)
        telnet = port == 23 or port <= 5000
        
        connection = self.connect_to.cisco_device(
            mgmt_ip, port, username, password, telnet=telnet
        )

        config_device = Configure(device_config=config, connection=connection)
        methods = [method for method in dir(Configure) \
            if not method.startswith("_") and not \
                "default_commands" == method
        ]

        print(f"Currently being configured: {hostname}")

        print("Initialising configuration...")
        config_device.default_commands()
        print("     Done!\n")

        for config_area in methods:
            print("Configuring "
                f"{config_area.replace('_', ' ').title()}..."
            )
            getattr(config_device, config_area)()
            print("    Done!\n")

        print("Configuration Complete!")

        for goodbye in ("end", "exit"):
            connection.send_command(goodbye, expect_string="")

if __name__ == "__main__":
    AutoConf().configure_cisco_device(
        hostname="R1",
        mgmt_ip="127.0.0.1",
        port=5000,
        username="admin",
        password="netautoconfig"
    )