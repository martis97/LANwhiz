from LANwhiz.config.base import BaseConfig
from LANwhiz.utils import Utilities


class DHCPPool(BaseConfig):
    """ Class for DHCP Pool configuration.
    
    Args:
        connection - Netmiko connection object
        config - DHCP Pool configuration
    """
    def __init__(self, connection, config, name):
        super().__init__(connection, config)
        self.utils.send_command(
            f"ip dhcp pool {name}"
        )

    def set_network(self):
        """ Defines DHCP pool's network and size """
        ip, cidr = self.config["network"].split("/")
        sm = Utilities.prefix_to_subnet_mask(int(cidr))
        self.utils.send_command(f"network {ip} {sm}")

    def set_default_gateway(self):
        """ Defines pool's default gateway """
        self.utils.send_command(
            f"default-router {self.config['default_gateway']}"
        )
    
    def set_dns(self):
        """ Define DNS addresses the pool will use """
        self.utils.send_command(f"dns-server {self.config['dns']}")