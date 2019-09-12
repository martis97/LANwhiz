from LANwhiz.utils import Utilities


class DHCPPool(object):
    def __init__(self, connection, config):
        self.connection = connection
        self.dhcp_config = config
        self.utils = Utilities(self.connection)
        self.utils.ensure_global_config_mode()
        self.utils.send_command(
            f"ip dhcp pool {self.dhcp_config['pool_name']}"
        )
    
    def set_network(self):
        """ Defines DHCP pool's network and size """
        ip, cidr = self.dhcp_config["network"].split("/")
        sm = self.utils.cidr_to_subnet_mask(cidr)
        self.utils.send_command(f"network {ip} {sm}")

    def set_default_gateway(self):
        """ Defines pool's default gateway """
        self.utils.send_command(
            f"default-router {self.dhcp_config['default_gateway']}"
        )
    
    def set_dns(self):
        """ Define DNS addresses the pool will use """
        self.utils.send_command(f"dns-server {self.dhcp_config['dns']}")