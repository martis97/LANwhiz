from LANwhiz.config.base import BaseConfig


class Interface(BaseConfig):
    def __init__(self, connection, config):
        super().__init__(connection, config)

    def ipv4(self):
        """ Sends command to configure IPv4 address """
        if self.config.get("ipv4"):
            ip, cidr = self.config["ipv4"].split("/")
            subnet_mask = self.utils.cidr_to_subnet_mask(int(cidr))
            ipv4_command = f"ip address {ip} {subnet_mask}"
            self.utils.send_command(ipv4_command)

    def ipv6(self):
        """ Sends commmand to configure IPv6 address """
        if self.config.get("ipv6"):
            ipv6_command = f"ipv6 address {self.config['ipv6']}"
            self.utils.send_command(ipv6_command)
    
    def description(self):
        """ Sends command to configure interface description """
        if self.config.get("description"):
            description = self.config["description"]
            self.utils.send_command(f"description {description}")

    def acl(self):
        """ Sends commands to configure ACLs on interfaces """
        acl_commands = []
        inbound = self.config["acl"].get("inbound")
        outbound = self.config["acl"].get("outbound")
        if inbound or outbound:
            for rule in outbound:
                acl_commands.append(f"ip access-group {rule} out")
            for rule in inbound:
                acl_commands.append(f"ip access-group {rule} in")
            for command in acl_commands:
                self.utils.send_command(command)

    def nat(self):
        """ Sends command to configure NAT on the interface """
        if self.config.get("nat"):
            nat_command = f"ip nat {self.config['nat']}"
            self.utils.send_command(nat_command)


class Line(BaseConfig):
    def __init__(self, connection, config):
        super().__init__(connection, config)

    def synchronous_logging(self):
        """ Enables Synchronous Logging on a line interface """
        self.utils.send_command("logging synchronous")

    def acl(self):
        """ Sends commands to configure ACLs on line interfaces """
        acl_commands = []
        inbound = self.config["acl"].get("inbound")
        outbound = self.config["acl"].get("outbound")
        for rule in outbound:
            acl_commands.append(f"access-class {rule} out")
        for rule in inbound:
            acl_commands.append(f"access-class {rule} in")
        for command in acl_commands:
            self.utils.send_command(command)
    
    def password(self):
        """ Configures a line interface with a password """
        if self.config.get("password"):
            self.utils.send_command(f"password {self.config['password']}")
            self.utils.send_command("login")