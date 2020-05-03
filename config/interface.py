from LANwhiz.config.base import BaseConfig
from LANwhiz.utils import Utilities



class Interface(BaseConfig):
    def __init__(self, connection, config, name, current):
        super().__init__(connection, config)
        self.current = current
        self.utils.ensure_global_config_mode()
        self.utils.send_command(f"interface {name}")


    def shutdown(self):
        if self.config.get("shutdown"):
            self.utils.send_command("shutdown")
        else:
            self.utils.send_command("no shutdown")

    def ipv4(self):
        """ Sends command to configure IPv4 address """
        if self.config.get("ipv4"):
            ip, cidr = self.config["ipv4"].split("/")
            subnet_mask = Utilities.prefix_to_subnet_mask(int(cidr))
            ipv4_command = f"ip address {ip} {subnet_mask}"
            self.utils.send_command(ipv4_command)
        else:
            self.utils.send_command("no ip address")

    def ipv6(self):
        """ Sends commmand to configure IPv6 address """
        if self.config.get("ipv6"):
            ipv6_command = f"ipv6 address {self.config['ipv6']}"
            self.utils.send_command(ipv6_command)
        else:
            self.utils.send_command("no ipv6 address")

    def description(self):
        """ Sends command to configure interface description """
        if self.config.get("description"):
            description = self.config["description"]
            self.utils.send_command(f"description {description}")
        else:
            self.utils.send_command("no description")

    def acl(self):
        """ Sends commands to configure ACLs on interfaces """
        current_acls = [cmd for cmd in self.current if "access-group" in cmd]
        acl_commands = []
        config = self.config.get("acl")

        if config:
            inbound, outbound = [config.get(acl) for acl in ("inbound", "outbound")]
        else:
            inbound, outbound = "", ""

        for rule in outbound:
            acl_commands.append(f"ip access-group {rule} out")
        for rule in inbound:
            acl_commands.append(f"ip access-group {rule} in")
        for command in acl_commands:
            if command not in current_acls:
                self.utils.send_command(command)
            else:
                current_acls.remove(command)
        # Remove deleted ACL assignments
        for remaining_acl in current_acls:
            self.utils.send_command(f"no {remaining_acl}")

    def nat(self):
        """ Sends command to configure NAT on the interface """
        if self.config.get("nat"):
            nat_command = f"ip nat {self.config['nat']}"
            self.utils.send_command(nat_command)
        else:
            self.utils.send_command("no ip nat inside")
            self.utils.send_command("no ip nat outside")
    
    def clock_rate(self):
        """ Sends command to configure clock rate of Serial interface """
        if self.config.get("clock_rate"):
            self.utils.send_command(f"clock rate {self.config['clock_rate']}")
    
    def bandwidth(self):
        if self.config.get("bandwidth"):
            self.utils.send_command(f"bandwidth {self.config['bandwidth']}")
        else:
            self.utils.send_command("no bandwidth")

    def other_config(self):
        """ Sends commands on interface config level """
        if self.config.get("other_commands"):
            for cmd in self.config["other_commands"]:
                self.utils.send_command(cmd)


class Line(BaseConfig):
    def __init__(self, connection, config, name):
        super().__init__(connection, config)
        self.current = self.utils.get_structured_config()[f"line {name}"]
        self.utils.ensure_global_config_mode()
        self.utils.send_command(f"line {name}")

    def synchronous_logging(self):
        """ Enables Synchronous Logging on a line interface """
        if self.config.get("logging synchronous"):
            self.utils.send_command("logging synchronous")
        else:
            self.utils.send_command("no logging synchronous")

    def acl(self):
        """ Sends commands to configure ACLs on interfaces """
        current_acls = [cmd for cmd in self.current if "access-group" in cmd]
        acl_commands = []
        config = self.config.get("acl")
        inbound, outbound = [config.get(acl, "") for acl in ("inbound", "outbound")]
        for rule in outbound:
            acl_commands.append(f"ip access-group {rule} out")
        for rule in inbound:
            acl_commands.append(f"ip access-group {rule} in")
        for command in acl_commands:
            if command not in current_acls:
                self.utils.send_command(command)
            else:
                current_acls.remove(command)
        # Remove deleted ACL assignments
        for remaining_acl in current_acls:
            self.utils.send_command(f"no {remaining_acl}")
    
    def password(self):
        """ Configures a line interface with a password """
        if self.config.get("password"):
            self.utils.send_command(f"password {self.config['password']}")
            self.utils.send_command("login")
        else:
            self.utils.send_command("no password")
            self.utils.send_command("no login")

    def other_commands(self):
        """ Sends commands on interface config level """
        if self.config.get("other_commands"):
            for cmd in self.config["other_commands"]:
                self.utils.send_command(cmd)