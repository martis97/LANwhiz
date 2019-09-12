import re
from net_auto_config.utils import Utilities


class Interface(object):
    def __init__(self, connection):
        self.connection = connection
        self.utils = Utilities(self.connection)

    def ipv4(self, ip):
        """ Sends command to configure IPv4 address """
        ipv4 = ip.split("/")[0]
        subnet_mask = self.utils.cidr_to_subnet_mask(int(ip.split("/")[1]))
        ipv4_command = f"ip address {ipv4} {subnet_mask}"
        self.connection.send_command(ipv4_command, expect_string="")

    def ipv6(self, ip):
        """ Sends commmand to configure IPv6 address """
        ipv6_command = f"ipv6 address {ip}"
        self.connection.send_command(ipv6_command, expect_string="")
    
    def description(self, description):
        """ Sends command to configure interface description """
        self.connection.send_command(
            f"description {description}",
            expect_string=""
        )

    def acl(self, interface, *, inbound=[], outbound=[]):
        """ Sends commands to configure ACLs on interfaces """
        acl_commands = []
        if inbound or outbound:
            for rule in outbound:
                acl_commands.append(f"ip access-group {rule} out")
            for rule in inbound:
                acl_commands.append(f"ip access-group {rule} in")
            for command in acl_commands:
                self.connection.send_command(command, expect_string="")

    def nat(self, direction):
        """ Sends command to configure NAT on the interface """
        nat_command = f"ip nat {direction}"
        self.connection.send_command(nat_command, expect_string="")


class Line(object):
    def __init__(self, connection):
        self.connection = connection
        self.utils = Utilities(self.connection)

    def synchronous_logging(self):
        """ Enables Synchronous Logging on a line interface """
        self.connection.send_command("logging synchronous", expect_string="")

    def acl(self, *, inbound=[], outbound=[]):
        """ Sends commands to configure ACLs on line interfaces """
        if inbound or outbound:
            acl_commands = []
            for rule in outbound:
                acl_commands.append(f"access-class {rule} out")
            for rule in inbound:
                acl_commands.append(f"access-class {rule} in")
            for command in acl_commands:
                self.connection.send_command(command, expect_string="")
    
    def password(self, password):
        """ Configures a line interface with a password """
        self.connection.send_command(
            f"password {password}",
            expect_string=""
        )
        self.connection.send_command("login", expect_string="")