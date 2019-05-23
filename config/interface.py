from net_auto_config.configure import Configure
from net_auto_config.utils import Utilities

class Interface():
    def __init__(self, connection):
        self.connection = connection
        self.utils = Utilities()

    def ipv4(self, ip):
        """ Sends command to configure IPv4 address """
        ipv4 = ip.split("/")[0]
        cidr = ip.split("/")[1]
        subnet_mask = self.utils.cidr_to_subnet_mask(cidr)
        ipv4_command = f"ip address {ipv4} {subnet_mask}"
        self.connection.send_command(ipv4_command)

    def ipv6(self, ip):
        """ Sends commmand to configure IPv6 address """
        ipv6_command = f"ipv6 address {ip}"
        self.connection.send_command(ipv6_command)

    def acl(self, interface, *, inbound, outbound):
        """ Sends commands to configure ACLs on interfaces """
        acl_commands = []
        for rule in outbound:
            acl_commands.append(f"ip access-group {rule} out")
        for rule in inbound:
            acl_commands.append(f"ip access-group {rule} in")
        for command in acl_commands:
            if "vty" in interface:
                for replacement in (("ip ", ""), ("group", "class")):
                    command = command.replace(*replacement)
            self.connection.send_command(command)

    def nat(self, direction):
        """ Sends command to configure NAT on the interface """
        nat_command = f"ip nat {direction}"
        self.connection.send_command(nat_command)