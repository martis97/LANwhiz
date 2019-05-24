"""
AutoConf Network Device Configuration Automation Platform
// Send configuration remotely //

Main Module
"""

from net_auto_config.connect import Connect
from net_auto_config.utils import Utilities
from net_auto_config.configure import Configure


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
        """ Adds and configures a Cisco Device """
        config = Utilities().read_config(hostname)
        for telnet_port in (23, 5000):
            if port == telnet_port:
                telnet = True
                break
            else:
                telnet = False

        connection = self.connect_to.cisco_device(
            mgmt_ip, port, username, password, telnet=telnet
        )

        config_device = Configure(device_config=config, connection=connection)
        config_device.interfaces()


if __name__ == "__main__":
    AutoConf().configure_cisco_device(
        hostname="R1",
        mgmt_ip="127.0.0.1",
        port=5000,
        username="admin",
        password="admin"
        
    )