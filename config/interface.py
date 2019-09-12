import re
from LANwhiz.utils import Utilities


class Interface(object):
    def __init__(self, connection):
        self.connection = connection
        self.utils = Utilities(self.connection)

    def ipv4(self, ip):
        """ Sends command to configure IPv4 address """
        ip, cidr = ip.split("/")
        subnet_mask = self.utils.cidr_to_subnet_mask(int(cidr))
        ipv4_command = f"ip address {ip} {subnet_mask}"
        self.utils.send_command(ipv4_command)

    def ipv6(self, ip):
        """ Sends commmand to configure IPv6 address """
        ipv6_command = f"ipv6 address {ip}"
        self.utils.send_command(ipv6_command)
    
    def description(self, description):
        """ Sends command to configure interface description """
        self.utils.send_command(f"description {description}")

    def acl(self, interface, *, inbound=[], outbound=[]):
        """ Sends commands to configure ACLs on interfaces """
        acl_commands = []
        if inbound or outbound:
            for rule in outbound:
                acl_commands.append(f"ip access-group {rule} out")
            for rule in inbound:
                acl_commands.append(f"ip access-group {rule} in")
            for command in acl_commands:
                self.utils.send_command(command)

    def nat(self, direction):
        """ Sends command to configure NAT on the interface """
        nat_command = f"ip nat {direction}"
        self.utils.send_command(nat_command)


class Line(object):
    def __init__(self, connection):
        self.connection = connection
        self.utils = Utilities(self.connection)

    def synchronous_logging(self):
        """ Enables Synchronous Logging on a line interface """
        self.utils.send_command("logging synchronous")

    def acl(self, *, inbound=[], outbound=[]):
        """ Sends commands to configure ACLs on line interfaces """
        if inbound or outbound:
            acl_commands = []
            for rule in outbound:
                acl_commands.append(f"access-class {rule} out")
            for rule in inbound:
                acl_commands.append(f"access-class {rule} in")
            for command in acl_commands:
                self.utils.send_command(command)
    
    def password(self, password):
        """ Configures a line interface with a password """
        self.utils.send_command(f"password {password}")
        self.utils.send_command("login")