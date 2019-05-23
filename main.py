"""
AutoConf Network Device Configuration Automation Platform
// Send unified configuration files platform-agnostically //

Main Module
"""

from net_auto_config.connect import Connect
from net_auto_config.utils import Utilities
from net_auto_config.configure import Configure


class AutoConf(object):
    def __init__(self):
        self.connect_to = Connect()

    def configure_cisco_device(self, hostname, mgmt_ip, username, password):
        """ Adds and configures a Cisco Device """
        config = Utilities().read_config(hostname)
        connection = self.connect_to.cisco_device(
            mgmt_ip, username, password
        )

        config_device = Configure(device_config=config, connection=connection)
        config_device.interfaces()


